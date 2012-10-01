"""
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_users
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.config import ManageClients, PUBLICATION_PREFS, PROJECTNAME
from bika.lims.content.person import Person
from bika.lims.interfaces import IPatient
from zope.interface import implements

schema = Person.schema.copy() + Schema((
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
    StringField('Gender',
        vocabulary=DisplayList((['m',_('Male')],
                                ['f',_('Female')])),
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

schema['JobTitle'].widget.visible = False
schema['Department'].widget.visible = False
schema['BusinessPhone'].widget.visible = False
schema['BusinessFax'].widget.visible = False
# Don't make title required - it will be computed from the Person's Fullname
schema['title'].required = 0
schema['title'].widget.visible = False

schema.moveField('PatientID', pos='top')
schema.moveField('PrimaryReferrer', after='Surname')
schema.moveField('Gender', after='PrimaryReferrer')

class Patient(Person):
    implements(IPatient)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the Fullname as title """
        return self.getFullname()

    security.declarePublic('getSamples')
    def getSamples(self):
        """ get all samples taken from this Patient """
        bc = getToolByName(self, 'bika_catalog')
        return [p.getObject() for p in bc(portal_type='Sample', getPatientUID=self.UID())]

    security.declarePublic('getARs')
    def getARs(self, analysis_state):
        bc = getToolByName(self, 'bika_catalog')
        return [p.getObject() for p in bc(portal_type='AnalysisRequest', getPatientUID=self.UID())]

atapi.registerType(Patient, PROJECTNAME)
