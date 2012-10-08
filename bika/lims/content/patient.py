"""
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_users
from Products.ATContentTypes.content import schemata
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims.browser.widgets import DateTimeWidget, RecordsWidget
from bika.lims.config import ManageClients, PUBLICATION_PREFS, PROJECTNAME, \
    GENDERS
from bika.lims.content.person import Person
from bika.lims.interfaces import IPatient
from bika.lims.permissions import *
from zope.interface import implements

schema = Person.schema.copy() + Schema((
    StringField('PatientID',
        searchable=1,
        required=1,
        widget=StringWidget(
            label=_('Patient ID'),
        ),
    ),
    ReferenceField('PrimaryReferrer',
        vocabulary='get_clients',
        allowed_types=('Client',),
        relationship='PatientClient',
        required=1,
        widget=SelectionWidget(
            format='select',
            label=_('Primary Referrer'),
        ),
    ),
    ComputedField('PrimaryReferrerUID',
        expression='here.getPrimaryReferrer() and here.getPrimaryReferrer().UID() or None',
        widget=ComputedWidget(
        ),
    ),
    StringField('Gender',
        vocabulary=GENDERS,
        index='FieldIndex',
        widget=SelectionWidget(
            format='select',
            label=_('Gender'),
        ),
    ),
    IntegerField('Age',
        widget=StringWidget(
            label=_('Age'),
        ),
    ),
    DateTimeField('BirthDate',
        required=1,
        widget=DateTimeWidget(
            label=_('Birth date'),
        ),
    ),
    BooleanField('BirthDateEstimated',
        default=False,
        widget=BooleanWidget(
            label=_('Birth date is estimated'),
        ),
    ),
    TextField('Remarks',
        searchable=True,
        default_content_type='text/x-web-intelligent',
        allowable_content_types=('text/x-web-intelligent',),
        default_output_type="text/html",
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_('Remarks'),
            append_only=True,
        ),
    ),
    RecordsField('TreatmentHistory',
        type='treatmenthistory',
        subfields=('Treatment', 'Drug', 'Start', 'End', 'Remarks'),
        required_subfields=('Treatment', 'Drug', 'Start', 'End'),
        subfield_labels={'Treatment':_('Treatment'), 'Drug': _('Drug'), 'Start':_('Start'),
                         'End': _('End'), 'Remarks': _('Remarks')},
        subfield_sizes={'Treatment':20, 'Drug':20, 'Start':10, 'End':10, 'Remarks':25},
        widget=RecordsWidget(
            label='Treatment History',
            description=_("A list of patient treatments and drugs administered."),
            visible = False, # uses view from browser/patient.py
        ),
    ),
    StringField('BirthPlace', schemata='Personal',
        widget=StringWidget(
            label=_('Birth place'),
        ),
    ),
    StringField('Ethnicity', schemata='Personal',
        index='FieldIndex',
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
schema['EmailAddress'].schemata = 'Personal'
schema['HomePhone'].schemata = 'Personal'
schema['MobilePhone'].schemata = 'Personal'
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

    def get_clients(self):
        ## Only show clients to which we have Manage AR rights.
        mtool = getToolByName(self, 'portal_membership')
        clientfolder = self.clients
        clients = []
        for client in clientfolder.objectValues("Client"):
            if not mtool.checkPermission(ManageAnalysisRequests, client):
                continue
            clients.append([client.UID(), client.Title()])
        return DisplayList(clients)

atapi.registerType(Patient, PROJECTNAME)
