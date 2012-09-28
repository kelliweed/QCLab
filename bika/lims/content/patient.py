"""The patient
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_users
from Products.ATExtensions.at_extensions import RecordWidget
from bika.lims.browser.widgets.datetimewidget import DateTimeWidget
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore import permissions
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from bika.lims import bikaMessageFactory as _, logger
from bika.lims.config import *
from bika.lims.content.contact import Contact

# Some pain here, to re-organise the Contact schematas for easier data input

schema = Schema((
    StringField('PatientID',
        searchable=1,
        required=1,
        widget=StringWidget(
            label=('Patient ID'),
        ),
    ),
    ReferenceField('PrimaryReferrer',
        allowed_types=('Client',),
        relationship='PatientClient',
        required=1,
        widget=ReferenceWidget(
            checkbox_bound=1,
            label='Primary Referrer',
        ),
    ),
    ComputedField('PrimaryReferrerUID',
        expression='here.getPrimaryReferrer() and here.getPrimaryReferrer().UID() or None',
        widget=ComputedWidget(
            visible=False,
        ),
    ),
)) + Contact.schema.copy() + Schema((
    StringField('Gender',
        vocabulary=GENDERS,
        index = 'FieldIndex',
        widget=SelectionWidget(
            label=_('Gender'),
        ),
    ),
    IntegerField('Age',
        widget=StringWidget(
            label=_('Age'),
        ),
    ),
    DateTimeField('BirthDate',
        required = 1,
        widget = DateTimeWidget(
            label=_('Birth date'),
        ),
    ),
    BooleanField('DOBEstimated',
        default=False,
        widget=BooleanWidget(
            label=_("Birth date estimated")
        ),
    ),
    TextField('Remarks',
        searchable = True,
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/html",
        widget = TextAreaWidget(
            macro = "bika_widgets/remarks",
            label = _('Remarks'),
            append_only = True,
        ),
    ),
    StringField('BirthPlace', schemata='Personal',
        widget=StringWidget(
            label=_('Birth place'),
        ),
    ),
    StringField('Ethnicity', schemata='Personal',
        index = 'FieldIndex',
        widget=StringWidget(
            label=_('Ethnicity'),
            description=_("Ethnicity eg. Asian, African, etc."),
        ),
    ),
    StringField('Citizenship', schemata='Personal',
        widget=StringWidget(
            label=_('Citizenship'),
        ),
    ),
    StringField('MothersName', schemata='Personal',
        widget=StringWidget(
            label=_('Mothers name'),
        ),
    ),
    StringField('CivilStatus', schemata='Personal',
        widget=StringWidget(
            label=_('Civil status'),
        ),
    ),
    ImageField('Photo', schemata='Identification',
        widget=ImageWidget(
            label=_('Photo'),
        ),
    ),
    ImageField('Feature', schemata='Identification',
        multiValue=1,
        widget=ImageWidget(
            label=_('Feature'),
        ),
    ),
))


# Don't make title required - it will be computed from the Person's Fullname
schema['title'].required = 0
for field_id in ('title', 'BusinessFax', 'JobTitle'):
    schema[field_id].required = 0
    schema[field_id].widget.visible = False

class Patient(Contact):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    # This is copied from Contact (In contact, it is acquired from Client)
    security.declarePublic('getCCContactsDisplayList')
    def getCCContactsDisplayList(self):
        pairs = []
        all_contacts = self.getContactsDisplayList().items()
        # remove myself
        for item in all_contacts:
            if item[0] != self.UID():
                pairs.append((item[0], item[1]))
        return DisplayList(pairs)

    def getPossibleAddresses(self):
        return ['PhysicalAddress', 'PostalAddress']

    security.declarePublic('getContactsDisplayList')
    def getContactsDisplayList(self):
        referrer = self.getPrimaryReferrer()
        if referrer:
            return referrer.getContactsDisplayList()
        else:
            return {}

    security.declarePublic('getContactUIDForUser')
    def getContactUIDForUser(self):
        """ Allows analysisrequest_add_form to support this context, not used yet (because patients arent users yet) """
        member = self.portal_membership.getAuthenticatedMember()
        user_id = member.getUserName()
        r = self.portal_catalog(portal_type='Contact', getUsername=user_id)
        if r:
            return r[0].UID

    security.declarePublic('getCCContacts')
    def getCCContacts(self):
        return self.getPrimaryReferrer().getCCContacts()

    security.declarePublic('getServices')
    def getServices(self):
        """ get all services in all ARs for this Patient """
        s_p = self.portal_catalog(portal_type='Sample',
                                 getPatientUID=self.UID())
        samples = []
        for sample in s_p:
            samples.append(sample.UID)

        ars = []
        ar_p = self.portal_catalog(portal_type='AnalysisRequest', getSampleUID=samples)
        these_services = {}
        for a in ar_p:
            ar = a.getObject()
            analyses = ar.getAnalyses()
            for analysis in analyses:
                if not these_services.has_key(analysis.Title()):
                    these_services[analysis.Title()] = analysis.getService()

        service_keys = these_services.keys()
        service_keys.sort()
        services = []
        for key in service_keys:
            services.append(these_services[key])
        return services

    security.declarePublic('getSamples')
    def getSamples(self):
        """ get all samples taken from this Patient """
        return [p.getObject() for p in self.portal_catalog(portal_type='Sample', getPatient=self.UID())]

    security.declarePublic('getARs')
    def getARs(self, analysis_state):
        ars = [ar for ar in self.objectValues('AnalysisRequest') if ar.getPatient().UID() == self.UID()]
        return ars

atapi.registerType(Patient, PROJECTNAME)
