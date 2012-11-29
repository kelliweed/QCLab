from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATContentTypes.utils import DT2dt
from Products.ATExtensions.ateapi import DateTimeField
from Products.ATExtensions.ateapi import RecordsField as RecordsField
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import CaseAetiologicAgentsWidget
from bika.lims.browser.widgets import CaseProvisionalDiagnosisWidget
from bika.lims.browser.widgets import CaseSymptomsWidget
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import PatientIdentifiersWidget
from bika.lims.browser.widgets import SplittedDateWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IBatch
from bika.lims.utils import isActive
from calendar import monthrange
from datetime import datetime, timedelta
from zope.interface import implements
import json
import plone

schema = BikaSchema.copy() + Schema((
    StringField('BatchID',
        searchable=True,
        required=0,
        validators=('uniquefieldvalidator',),
        widget=StringWidget(
            visible = False,
            label=_("Batch ID"),
        )
    ),
    StringField('ClientBatchID',
        searchable=True,
        required=0,
        widget=StringWidget(
            label=_("Client Batch ID")
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
        required=1,
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
        required=0,
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
    DateTimeField('OnsetDate',
          widget=DateTimeWidget(
              label=_('Onset Date'),
          ),
    ),
    StringField('PatientBirthDate',
          widget=StringWidget(
              visible={'view': 'hidden', 'edit': 'hidden' },
          ),
    ),
    RecordsField('PatientAgeAtCaseOnsetDate',
        widget=SplittedDateWidget(
            label=_('Patient Age at Case Onset Date'),
        ),
    ),
    BooleanField('OnsetDateEstimated',
        default=False,
        widget=BooleanWidget(
            label = _("Onset Date Estimated"),
        ),
    ),
    
    RecordsField('ProvisionalDiagnosis',
        type='provisionaldiagnosis',
        subfields=('Code', 'Title', 'Description', 'Onset', 'Remarks'),
        subfield_sizes={'Code': 7, 'Title': 15, 'Description': 25, 'Onset': 10, 'Remarks': 25},
        widget=CaseProvisionalDiagnosisWidget(
            label='Provisional diagnosis',
        ),
    ),

    TextField('AdditionalNotes',
        default_content_type='text/x-web-intelligent',
        allowable_content_types=('text/x-web-intelligent',),
        default_output_type="text/html",
        widget=TextAreaWidget(
            label=_('Additional notes'),
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
    RecordsField('AetiologicAgents',
        type='aetiologicagents',
        subfields=('Code', 'Title', 'Description', 'Onset', 'Remarks'),
        subfield_sizes={'Title': 15, 'Description': 25, 'Subtype': 10, 'Remarks': 25},
        widget=CaseAetiologicAgentsWidget(
            label='Aetiologic Agents',
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
schema.moveField('BatchLabels', after='AdditionalNotes')
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
        p_uid = self.getPatientUID()
        if p_uid:
            bpc = getToolByName(self, 'bika_patient_catalog')
            patient = bpc(UID=p_uid)
            if patient:
                res = "%s (%s)" % (res, patient[0].Title)
        return str(res).decode('utf-8').encode('utf-8')

    security.declarePublic('getBatchID')
    def getBatchID(self):
        return self.getId()

    def getContacts(self, dl=True):
        pc = getToolByName(self, 'portal_catalog')
        bc = getToolByName(self, 'bika_catalog')
        bsc = getToolByName(self, 'bika_setup_catalog')
        bpc = getToolByName(self, 'bika_patient_catalog')
        pairs = []
        objects = []
        client = None
        # Try get Client
        c_uid = self.getClientUID()
        if c_uid:
            client = pc(UID=c_uid)[0].getObject()
            for contact in client.objectValues('Contact'):
                if isActive(contact):
                    pairs.append((contact.UID(), contact.Title()))
                    if not dl:
                        objects.append(contact)
        # Try get Patient/PrimaryReferrer
        p_uid = self.getPatientUID()
        if p_uid:
            patient = bpc(UID=p_uid)[0].getObject()
            if patient:
                pr = patient.getPrimaryReferrer()
                if pr and pr.UID() != client.UID():
                    for contact in pr.objectValues('Contact'):
                        if isActive(contact):
                            pairs.append((contact.UID(), contact.Title()))
                            if not dl:
                                objects.append(contact)
        if pairs:
            pairs.sort(lambda x, y:cmp(x[1].lower(), y[1].lower()))
            return dl and DisplayList(pairs) or objects
        # fallback to LabContacts
        for contact in bsc(portal_type = 'LabContact',
                           inactive_state = 'active',
                           sort_on = 'sortable_title'):
            pairs.append((contact.UID, contact.Title))
            if not dl:
                objects.append(contact.getObject())
        return dl and DisplayList(pairs) or objects

    def getCCs(self):
        items = []
        for contact in self.getContacts(dl=False):
            item = {'uid': contact.UID(), 'title': contact.Title()}
            ccs = []
            if hasattr(contact, 'getCCContact'):
                for cc in contact.getCCContact():
                    if isActive(cc):
                        ccs.append({'title': cc.Title(),
                                    'uid': cc.UID(),})
            item['ccs_json'] = json.dumps(ccs)
            item['ccs'] = ccs
            items.append(item)
        items.sort(lambda x, y:cmp(x['title'].lower(), y['title'].lower()))
        return items

    def getOnsetDate(self):
        """ Return OnsetDate, but calculate it first if it's not set
        """
        osd = self.getField('OnsetDate').get(self)
        if not osd:
            osd = self.estOnsetDate()
            self.setOnsetDate(osd)
        return osd

    def estOnsetDate(self):
        """ If onset date is not specified, we estimate it.
        we use the earliest 'DateSampled' or 'DateReceived'
        value for samples in this batch.
        """
        earliest = DateTime()
        found = 0
        swe = self.bika_setup.getSamplingWorkflowEnabled()
        for ar in self.getAnalysisRequests():
            sample = ar.getSample()
            if swe:
                d = sample.getDateSampled()
                if d and d < earliest:
                    earliest = d
                    found = 1
            d = ar.getDateReceived()
            if d and d < earliest:
                earliest = d
                found = 1
        if found:
            return earliest

    # This is copied from Client (Contact acquires it, but we do not)
    security.declarePublic('getContactsDisplayList')
    def getContactsDisplayList(self):
        pc = getToolByName(self, 'portal_catalog')
        pairs = []
        for contact in pc(portal_type = 'Doctor', inactive_state = 'active'):
            pairs.append((contact.UID, contact.Title))
        patient = self.getPatient()
        pr = patient and patient.getPrimaryReferrer() or None
        if pr:
            for contact in pc(portal_type = 'Contact', inactive_state = 'active', getClientUID = pr):
                pairs.append((contact.UID, contact.Title))
        for contact in pc(portal_type = 'LabContact', inactive_state = 'active'):
            pairs.append((contact.UID, contact.Title))
        # sort the list by the second item
        pairs.sort(lambda x, y:cmp(x[1], y[1]))
        return DisplayList(pairs)

    # This is copied from Contact (In contact, it refers to the parent's
    # getContactsDisplayList, while we define our own (our client's)
    security.declarePublic('getCCContactsDisplayList')
    def getCCContactsDisplayList(self):
        contacts = []
        pc = getToolByName(self, 'portal_catalog')
        client = pc(portal_type='Client', UID=self.getClientUID())
        if client:
            return client[0].getObject().getCCContacts()
        else:
            patient = self.getPatient()
            pr = patient and patient.getPrimaryReferrer() or None
            return DisplayList(pr and pr.getCCContacts() or [])


            ccs = []
            if hasattr(contact, 'getCCContact'):
                for cc in contact.getCCContact():
                    if isActive(cc):
                        ccs.append({'title': cc.Title(),
                                    'uid': cc.UID(),})
            item['ccs_json'] = json.dumps(ccs)
            item['ccs'] = ccs
            items.append(item)
        items.sort(lambda x, y:cmp(x['title'].lower(), y['title'].lower()))
        return items

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
        uid = self.UID()
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
        pc = getToolByName(self, 'portal_catalog')
        if type(value) in (list, tuple):
            value = value[0]
        if value:
            if type(value) == str:
                value = pc(portal_type='Doctor', getDoctorID=value)[0].getObject()
            return self.setDoctorUID(value.UID())

    def setPatientID(self, value):
        self.Schema()['PatientID'].set(self, value)
        bpc = getToolByName(self, 'bika_patient_catalog')
        if type(value) in (list, tuple):
            value = value[0]
        if value:
            if type(value) == str:
                value = bpc(portal_type='Patient', getPatientID=value)[0].getObject()
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

    def getPatientIdentifiers(self):
        bpc = getToolByName(self, 'bika_patient_catalog')
        patient = bpc(UID=self.getPatientUID())
        if patient:
            return patient[0].getObject().getPatientIdentifiers()

    def getPatientIdentifiersStr(self):
        bpc = getToolByName(self, 'bika_patient_catalog')
        patient = bpc(UID=self.getPatientUID())
        if patient:
            patient = patient[0].getObject()
            return patient.getPatientIdentifiersStr()

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

    def getPatientBirthDate(self):
        bpc = getToolByName(self, 'bika_patient_catalog')
        patient = bpc(UID=self.getPatientUID())
        if patient:
            patient = patient[0].getObject()
            return patient.getBirthDate()

    def getPatientAgeAtCaseOnsetDate(self):
        bpc = getToolByName(self, 'bika_patient_catalog')
        patient = bpc(UID=self.getPatientUID())
        if patient and self.getOnsetDate():
            patient = patient[0].getObject()
            dob = DT2dt(patient.getBirthDate()).replace(tzinfo=None)
            now = DT2dt(self.getOnsetDate()).replace(tzinfo=None)

            currentday = now.day
            currentmonth = now.month
            currentyear = now.year
            birthday = dob.day
            birthmonth = dob.month
            birthyear = dob.year
            ageday = currentday-birthday
            agemonth = 0
            ageyear = 0
            months31days = [1,3,5,7,8,10,12]

            if (ageday < 0):
                currentmonth-=1
                if (currentmonth < 1):
                    currentyear-=1
                    currentmonth = currentmonth + 12;

                dayspermonth = 30;
                if currentmonth in months31days:
                    dayspermonth = 31;
                elif currentmonth == 2:
                    dayspermonth = 28
                    if(currentyear % 4 == 0
                       and (currentyear % 100 > 0 or currentyear % 400==0)):
                        dayspermonth += 1

                ageday = ageday + dayspermonth

            agemonth = currentmonth - birthmonth
            if (agemonth < 0):
                currentyear-=1
                agemonth = agemonth + 12

            ageyear = currentyear - birthyear

            return {'year':ageyear,
                    'month':agemonth,
                    'day':ageday}
        else:
            return {'year':'',
                    'month':'',
                    'day':''}

registerType(Batch, PROJECTNAME)
