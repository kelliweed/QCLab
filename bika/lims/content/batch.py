from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.ATExtensions.ateapi import DateTimeField
from Products.ATExtensions.ateapi import RecordsField as RecordsField
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import CaseSymptomsWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IBatch
from bika.lims.utils import isActive
from zope.interface import implements
import plone
import json

schema = BikaSchema.copy() + Schema((
    StringField('BatchID',
        searchable=True,
        required=1,
        validators=('uniquefieldvalidator',),
        widget=StringWidget(
            label=_("Batch ID"),
        )
    ),
    LinesField('BatchLabels',
        vocabulary = "BatchLabelVocabulary",
        widget=MultiSelectionWidget(
            label=_("Batch labels"),
            format="checkbox",
        )
    ),
    StringField('ClientID',
        widget=StringWidget(
            label=_("Client"),
        )
    ),
    StringField('ClientUID',
        widget=StringWidget(
            visible=False,
        ),
    ),
    StringField('DoctorID',
        widget=StringWidget(
            label=_("Doctor"),
        )
    ),
    StringField('DoctorUID',
        widget=StringWidget(
            visible=False,
        ),
    ),
    StringField('PatientID',
        required = 1,
        widget=StringWidget(
            label=_('Patient'),
        ),
    ),
    StringField('PatientUID',
        widget=StringWidget(
            visible=False,
        ),
    ),
    DateTimeField('DateOfOnset',
          widget=DateTimeWidget(
              label=_('Date of onset of illness'),
          ),
      ),
    TextField('ProvisionalDiagnosis',
        default_content_type='text/x-web-intelligent',
        allowable_content_types=('text/x-web-intelligent',),
        default_output_type="text/html",
        widget=TextAreaWidget(
            label=_('Provisional Diagnosis and additional notes'),
        ),
    ),
    StringField('CaseStatus',
        vocabulary='getCaseStatuses',
        widget=MultiSelectionWidget(
            format='checkbox',
            label=_("Case status")
        ),
    ),
    StringField('CaseOutcome',
        vocabulary='getCaseOutcomes',
        widget=MultiSelectionWidget(
            format='checkbox',
            label=_("Case outcome")
        ),
    ),
    RecordsField('Symptoms',
        type='symptoms',
        subfields=('Code', 'Title', 'Description', 'Onset', 'Remarks'),
        subfield_sizes={'Code': 7, 'Title': 15, 'Description': 25, 'Onset': 10, 'Remarks': 25},
        widget=CaseSymptomsWidget(
            label='Signs and Symptoms',
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
        )
    )
)
)

schema['title'].required = False
schema['title'].widget.visible = False
schema.moveField('BatchLabels', after='ProvisionalDiagnosis')
schema.moveField('PatientID', after='BatchID')

class Batch(BaseContent):
    implements(IBatch)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def _getCatalogTool(self):
        from bika.lims.catalog import getCatalog
        return getCatalog(self)

    def Title(self):
        """ Return the BatchID or id as title """
        res = self.getBatchID()
        return str(res).encode('utf-8')

    security.declarePublic('getCCContacts')
    def getCCContacts(self):
        """ Return JSON containing all Lab contacts (with empty default CC lists).
        This function is used to set form values for javascript.
        """
        contact_data = []
        for contact in self.bika_setup.bika_labcontacts.objectValues('LabContact'):
            if isActive(contact):
                this_contact_data = {'title': contact.Title(),
                                     'uid': contact.UID(), }
                ccs = []
                if hasattr(contact, 'getCCContact'):
                    for cc in contact.getCCContact():
                        if isActive(cc):
                            ccs.append({'title': cc.Title(),
                                        'uid': cc.UID(),})
                this_contact_data['ccs_json'] = json.dumps(ccs)
                this_contact_data['ccs'] = ccs
            contact_data.append(this_contact_data)
        contact_data.sort(lambda x, y:cmp(x['title'].lower(),
                                          y['title'].lower()))
        return contact_data

    def BatchLabelVocabulary(self):
        """ return all batch labels """
        bsc = getToolByName(self, 'bika_setup_catalog')
        ret = []
        for p in bsc(portal_type = 'BatchLabel',
                      inactive_state = 'active',
                      sort_on = 'sortable_title'):
            ret.append((p.UID, p.Title))
        return DisplayList(ret)

    def getAnalysisRequests(self):
        bc = getToolByName(self, 'bika_catalog')
        uid = self.context.UID()
        return [b.getObject() for b in bc(portal_type='AnalysisRequest',
                                          getBatchUID=uid)]
    def getCaseStatuses(self):
        """ return all Case Statuses from site setup """
        bsc = getToolByName(self, 'bika_setup_catalog')
        ret = []
        for b in bsc(portal_type='CaseStatus',
                     inactive_state='active',
                     sort_on='sortable_title'):
            ret.append((b.Title, b.Title))
        return DisplayList(ret)

    def getCaseOutcomes(self):
        """ return all Case Outcomes from site setup """
        bsc = getToolByName(self, 'bika_setup_catalog')
        ret = []
        for b in bsc(portal_type='CaseOutcome',
                     inactive_state='active',
                     sort_on='sortable_title'):
            ret.append((b.Title, b.Title))
        return DisplayList(ret)

    def setClientID(self, value):
        self.Schema()['ClientID'].set(self, value)
        pc = getToolByName(self, 'portal_catalog')
        if type(value) in (list, tuple):
            value = value[0]
        if value:
            if type(value) == str:
                value = pc(portal_type='Client', getClientID=value)[0].getObject()
            return self.setClientUID(value.UID())

    def setDoctorID(self, value):
        self.Schema()['DoctorID'].set(self, value)
        bc = getToolByName(self, 'bika_catalog')
        if type(value) in (list, tuple):
            value = value[0]
        if value:
            if type(value) == str:
                value = bc(portal_type='Doctor', getDoctorID=value)[0].getObject()
            return self.setDoctorUID(value.UID())

    def setPatientID(self, value):
        self.Schema()['PatientID'].set(self, value)
        bpc = getToolByName(self, 'bika_patient_catalog')
        if type(value) in (list, tuple):
            value = value[0]
        if value:
            if type(value) == str:
                print value
                value = bpc(portal_type='Patient', title=value)[0].getObject()
            return self.setPatientUID(value.UID())

    def setChronicConditions(self, value):
        bpc = getToolByName(self, 'bika_patient_catalog')
        patient = bpc(UID=self.getPatientUID())
        if patient:
            patient = patient[0].getObject()
            return patient.setChronicConditions(value)

    def getChronicConditions(self):
        bpc = getToolByName(self, 'bika_patient_catalog')
        patient = bpc(UID=self.getPatientUID())
        if patient:
            patient = patient[0].getObject()
            return patient.getChronicConditions()

    def setTreatmentHistory(self, value):
        bpc = getToolByName(self, 'bika_patient_catalog')
        patient = bpc(UID=self.getPatientUID())
        if patient:
            patient = patient[0].getObject()
            return patient.setTreatmentHistory(value)

    def getTreatmentHistory(self):
        bpc = getToolByName(self, 'bika_patient_catalog')
        patient = bpc(UID=self.getPatientUID())
        if patient:
            patient = patient[0].getObject()
            return patient.getTreatmentHistory()

    def setImmunizationHistory(self, value):
        bpc = getToolByName(self, 'bika_patient_catalog')
        patient = bpc(UID=self.getPatientUID())
        if patient:
            patient = patient[0].getObject()
            return patient.setImmunizationHistory(value)

    def getImmunizationHistory(self):
        bpc = getToolByName(self, 'bika_patient_catalog')
        patient = bpc(UID=self.getPatientUID())
        if patient:
            patient = patient[0].getObject()
            return patient.getImmunizationHistory()

    def setTravelHistory(self, value):
        bpc = getToolByName(self, 'bika_patient_catalog')
        patient = bpc(UID=self.getPatientUID())
        if patient:
            patient = patient[0].getObject()
            return patient.setTravelHistory(value)

    def getTravelHistory(self):
        bpc = getToolByName(self, 'bika_patient_catalog')
        patient = bpc(UID=self.getPatientUID())
        if patient:
            patient = patient[0].getObject()
            return patient.getTravelHistory()

registerType(Batch, PROJECTNAME)
