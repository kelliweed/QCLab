from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.AdvancedQuery import Or, MatchRegexp, Between
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import PMF, logger, bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.analysisrequest import AnalysisRequestWorkflowAction, \
    AnalysisRequestsView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.client import ClientAnalysisRequestsView, \
    ClientSamplesView
from bika.lims.browser.publish import Publish
from bika.lims.browser.sample import SamplesView
from bika.lims.content.treatment import getTreatmentTypes
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IContacts
from bika.lims.permissions import *
from bika.lims.subscribers import doActionFor, skip
from bika.lims.utils import isActive
from bika.lims.icd9cm import icd9_codes
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.i18n import translate
from zope.interface import implements
import json
import plone

class PatientAnalysisRequestsView(AnalysisRequestsView):
    def __init__(self, context, request):
        super(PatientAnalysisRequestsView, self).__init__(context, request)
        self.contentFilter['getPatientUID'] = self.context.UID()
    def __call__(self):
        self.context_actions = {}
        wf = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')
        addPortalMessage = self.context.plone_utils.addPortalMessage
        PR = self.context.getPrimaryReferrer()
        if isActive(self.context):
            if mtool.checkPermission(AddAnalysisRequest, PR):
                self.context_actions[self.context.translate(_('Add'))] = {
                    'url':self.context.absolute_url()+'/ar_add',
                    'icon': '++resource++bika.lims.images/add.png'}
        return super(PatientAnalysisRequestsView, self).__call__()

class PatientSamplesView(SamplesView):
    def __init__(self, context, request):
        super(PatientSamplesView, self).__init__(context, request)
        self.contentFilter['getPatientUID'] = self.context.UID()

class TreatmentHistoryView(BrowserView):
    """ bika listing to display Treatment History for a
        TreatmentHistory field.
    """

    template = ViewPageTemplateFile("templates/patient_treatmenthistory.pt")

    def __call__(self):

        if self.request.form.has_key('clear'):
            # Clear treatment history
            self.context.setTreatmentHistory([])
            self.context.plone_utils.addPortalMessage(PMF("Treatment history cleared"))

        elif self.request.form.has_key('delete'):
            # Delete selected treatments
            tre = self.context.getTreatmentHistory()
            new = []
            for i in range(len(tre)):
                if (not self.request.form.has_key('SelectItem-%s'%i)):
                    new.append(tre[i])
            self.context.setTreatmentHistory(new)
            self.context.plone_utils.addPortalMessage(PMF("Selected treatments deleted"))

        elif 'submitted' in self.request:
            bsc = self.bika_setup_catalog
            new = len(self.context.getTreatmentHistory())>0 and self.context.getTreatmentHistory() or []
            for t in range(len(self.request.form['Treatment'])):
                T = self.request.form['Treatment'][t]
                D = self.request.form['Drug'][t]
                S = self.request.form['Start'][t]
                E = self.request.form['End'][t]
                # Create new Treatment entry if none exists
                Tlist = bsc(portal_type='Treatment', title=T)
                if not Tlist:
                    folder = self.context.bika_setup.bika_treatments
                    _id = folder.invokeFactory('Treatment', id = 'tmp')
                    obj = folder[_id]
                    obj.edit(title = T)
                    obj.unmarkCreationFlag()
                    renameAfterCreation(obj)
                # Create new Drug entry if none exists
                Dlist = bsc(portal_type='Drug', title=D)
                if not Dlist:
                    folder = self.context.bika_setup.bika_drugs
                    _id = folder.invokeFactory('Drug', id = 'tmp')
                    obj = folder[_id]
                    obj.edit(title = D)
                    obj.unmarkCreationFlag()
                    renameAfterCreation(obj)
                new.append({'Treatment':T, 'Drug':D, 'Start':S, 'End':E})
            self.context.setTreatmentHistory(new)
            self.context.plone_utils.addPortalMessage(PMF("Changes saved"))
        return self.template()

    def hasTreatmentHistory(self):
        return len(self.context.getTreatmentHistory())>0

class AllergiesView(BrowserView):
    """ bika listing to display Allergies for Drug Prohibitions
    """

    template = ViewPageTemplateFile("templates/patient_allergies.pt")

    def __call__(self):

        if self.request.form.has_key('clear'):
            # Clear allergies
            self.context.setAllergies([])
            self.context.plone_utils.addPortalMessage(PMF("Allergies cleared"))

        elif self.request.form.has_key('delete'):
            # Delete selected allergies
            als = self.context.getAllergies()
            new = []
            for i in range(len(als)):
                if (not self.request.form.has_key('SelectItem-%s'%i)):
                    new.append(als[i])
            self.context.setAllergies(new)
            self.context.plone_utils.addPortalMessage(PMF("Selected allergies deleted"))

        elif 'submitted' in self.request:
            bsc = self.bika_setup_catalog
            new = len(self.context.getAllergies())>0 and self.context.getAllergies() or []
            for p in range(len(self.request.form['DrugProhibition'])):
                P = self.request.form['DrugProhibition'][p]
                D = self.request.form['Drug'][p]

                # Create new Allergy entry if none exists
                Plist = bsc(portal_type='DrugProhibition', title=P)
                if not Plist:
                    folder = self.context.bika_setup.bika_drugprohibitions
                    _id = folder.invokeFactory('DrugProhibition', id = 'tmp')
                    obj = folder[_id]
                    obj.edit(title = P)
                    obj.unmarkCreationFlag()
                    renameAfterCreation(obj)
                # Create new Drug entry if none exists
                Dlist = bsc(portal_type='Drug', title=D)
                if not Dlist:
                    folder = self.context.bika_setup.bika_drugs
                    _id = folder.invokeFactory('Drug', id = 'tmp')
                    obj = folder[_id]
                    obj.edit(title = D)
                    obj.unmarkCreationFlag()
                    renameAfterCreation(obj)
                new.append({'DrugProhibition':P, 'Drug':D})
            self.context.setAllergies(new)
            self.context.plone_utils.addPortalMessage(PMF("Changes saved"))
        return self.template()

    def hasAllergies(self):
        return len(self.context.getAllergies())>0

class ImmunizationHistoryView(BrowserView):
    """ bika listing to display Immunization history
    """

    template = ViewPageTemplateFile("templates/patient_immunizationhistory.pt")

    def __call__(self):

        if self.request.form.has_key('clear'):
            # Clear immunization history
            self.context.setImmunizationHistory([])
            self.context.plone_utils.addPortalMessage(PMF("Immunization history cleared"))

        elif self.request.form.has_key('delete'):
            # Delete selected allergies
            imh = self.context.getImmunizationHistory()
            new = []
            for i in range(len(imh)):
                if (not self.request.form.has_key('SelectItem-%s'%i)):
                    new.append(imh[i])
            self.context.setImmunizationHistory(new)
            self.context.plone_utils.addPortalMessage(PMF("Selected immunizations deleted"))

        elif 'submitted' in self.request:
            bsc = self.bika_setup_catalog
            new = len(self.context.getImmunizationHistory())>0 and self.context.getImmunizationHistory() or []
            E = self.request.form['EPINumber']
            for i in range(len(self.request.form['Immunization'])):
                I = self.request.form['Immunization'][i]
                V = self.request.form['VaccinationCenter'][i]
                D = self.request.form['Date'][i]

                # Create new Immunization entry if none exists
                if (len(I.strip())>0):
                    ilist = bsc(portal_type='Immunization', title=I)
                    if not ilist:
                        folder = self.context.bika_setup.bika_immunizations
                        _id = folder.invokeFactory('Immunization', id='tmp')
                        obj = folder[_id]
                        obj.edit(title = I)
                        obj.unmarkCreationFlag()
                        renameAfterCreation(obj)

                # Create new VaccinationCenter entry if none exists
                if (len(V.strip())>0):
                    Vlist = bsc(portal_type='VaccinationCenter', title=V)
                    if not Vlist:
                        folder = self.context.bika_setup.bika_vaccinationcenters
                        _id = folder.invokeFactory('VaccinationCenter', id='tmp')
                        obj = folder[_id]
                        obj.edit(Name = V)
                        obj.unmarkCreationFlag()
                        renameAfterCreation(obj)

                new.append({'EPINumber':E, 'Immunization':I, 'VaccinationCenter':V, 'Date':D})

            self.context.setImmunizationHistory(new)
            self.context.plone_utils.addPortalMessage(PMF("Changes saved"))
        return self.template()

    def getEPINumber(self):
        ih = self.context.getImmunizationHistory()
        return (len(ih) > 0 and 'EPINumber' in ih[0]) and ih[0]['EPINumber'] or ''

    def hasImmunizationHistory(self):
        return len(self.context.getImmunizationHistory())>0

class ChronicConditionsView(BrowserView):
    """ bika listing to display Chronic Conditions
    """

    template = ViewPageTemplateFile("templates/patient_chronicconditions.pt")

    def __call__(self):
        if self.request.form.has_key('clear'):
            self.context.setChronicConditions([])
            self.context.plone_utils.addPortalMessage(PMF("Chronic conditions cleared"))

        elif self.request.form.has_key('delete'):
            imh = self.context.getChronicConditions()
            new = []
            for i in range(len(imh)):
                if (not self.request.form.has_key('SelectItem-%s'%i)):
                    new.append(imh[i])
            self.context.setChronicConditions(new)
            self.context.plone_utils.addPortalMessage(PMF("Selected chronic conditions deleted"))

        elif 'submitted' in self.request:
            bsc = self.bika_setup_catalog
            new = len(self.context.getChronicConditions())>0 and self.context.getChronicConditions() or []
            for i in range(len(self.request.form['Title'])):
                C = self.request.form['Code'][i]
                S = self.request.form['Title'][i]
                D = self.request.form['Description'][i]
                O = self.request.form['Onset'][i]
                
                # Only allow to create entry if the selected symptom exists 
                Slist = bsc(portal_type='Symptom', title=S, code=C)
                ISlist = [x for x in icd9_codes['R']
                          if x['code'] == C
                          and x['short'] == S
                          and x['long'] == D]
                if not Slist and not ISlist:
                    self.context.plone_utils.addPortalMessage(_("The chronic condition symptom '%s' is not valid") % S, "error")
                else:
                    new.append({'Code':C, 'Title':S, 'Description':D, 'Onset': O})          
                      
            self.context.setChronicConditions(new)
            self.context.plone_utils.addPortalMessage(PMF("Changes saved"))     
        return self.template()

    def hasChronicConditions(self):
        return len(self.context.getChronicConditions())>0

class TravelHistoryView(BrowserView):
    """ bika listing to display Travel history
    """

    template = ViewPageTemplateFile("templates/patient_travelhistory.pt")

    def __call__(self):

        if self.request.form.has_key('clear'):
            # Clear travel history
            self.context.setTravelHistory([])
            self.context.plone_utils.addPortalMessage(PMF("Travel history cleared"))

        elif self.request.form.has_key('delete'):
            # Delete selected allergies
            imh = self.context.getTravelHistory()
            new = []
            for i in range(len(imh)):
                if (not self.request.form.has_key('SelectItem-%s'%i)):
                    new.append(imh[i])
            self.context.setTravelHistory(new)
            self.context.plone_utils.addPortalMessage(PMF("Selected travels deleted"))

        elif 'submitted' in self.request:
            new = len(self.context.getTravelHistory())>0 and self.context.getTravelHistory() or []
            for i in range(len(self.request.form['TripStartDate'])):
                S = self.request.form['TripStartDate'][i]
                E = self.request.form['TripEndDate'][i]
                T = self.request.form['Country'][i]
                L = self.request.form['Location'][i]

                new.append({'TripStartDate':S, 'TripEndDate':E, 'Country': T, 'Location': L})

            self.context.setTravelHistory(new)
            self.context.plone_utils.addPortalMessage(PMF("Changes saved"))
        return self.template()

    def hasTravelHistory(self):
        return len(self.context.getTravelHistory())>0

class ajaxGetPatients(BrowserView):
    """ Patient vocabulary source for jquery combo dropdown box
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = self.request['searchTerm'].lower()
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']

        rows = []

        # lookup patient objects from ZODB
        # AdvancedQuery is faster, but requires whole words.
        # if searchTerm and len(searchTerm) < 3:
        #     return json.dumps(rows)
        # We'll have to do something else to make this acceptable.
        # aq = MatchRegexp('Title', "%s" % searchTerm) | \
        #      MatchRegexp('Description', "%s" % searchTerm) | \
        #      MatchRegexp('getPatientID', "%s" % searchTerm)
        # brains = self.bika_patient_catalog.evalAdvancedQuery(aq)

        bpc = self.bika_patient_catalog
        proxies = bpc(portal_type='Patient')
        for patient in proxies:
            # Also search across additional identifiers
            addidfound = False
            addids = patient.getObject().getPatientIdentifiers()       
            for addid in addids:
                if addid['Identifier'].lower().find(searchTerm) > -1:
                    addidfound = True
                    break
                
            if patient.Title.lower().find(searchTerm) > -1 \
            or patient.getPatientID.lower().find(searchTerm) > -1 \
            or addidfound:
                patient = patient.getObject()
                rows.append({'Title': patient.Title() or '',
                         'PatientID': patient.getPatientID(),
                         'PrimaryReferrer': patient.getPrimaryReferrer().Title(),
                         'PatientUID': patient.UID(),
                         'AdditionalIdentifiers':patient.getPatientIdentifiersStr()})

        rows = sorted(rows, cmp=lambda x,y: cmp(x.lower(), y.lower()), key=itemgetter(sidx and sidx or 'Title'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page':page,
               'total':pages,
               'records':len(rows),
               'rows':rows[ (int(page) - 1) * int(nr_rows) : int(page) * int(nr_rows) ]}

        return json.dumps(ret)

class ajaxGetDrugs(BrowserView):
    """ Drug vocabulary source for jquery combo dropdown box
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = self.request['searchTerm'].lower()
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        rows = []

        # lookup objects from ZODB
        brains = self.bika_setup_catalog(portal_type = 'Drug')
        if brains and searchTerm:
            brains = [p for p in brains if p.Title.lower().find(searchTerm) > -1]

        for p in brains:
            rows.append({'Title': p.Title})

        rows = sorted(rows, cmp=lambda x,y: cmp(x.lower(), y.lower()), key=itemgetter(sidx and sidx or 'Title'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page':page,
               'total':pages,
               'records':len(rows),
               'rows':rows[ (int(page) - 1) * int(nr_rows) : int(page) * int(nr_rows) ]}

        return json.dumps(ret)

class ajaxGetTreatments(BrowserView):
    """ Treatment vocabulary source for jquery combo dropdown box
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = self.request['searchTerm'].lower()
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        rows = []

        # lookup objects from ZODB
        brains = self.bika_setup_catalog(portal_type = 'Treatment')
        if brains and searchTerm:
            brains = [p for p in brains if p.Title.lower().find(searchTerm) > -1]

        TTypes = getTreatmentTypes(self.context)

        for p in brains:
            o = p.getObject()
            ttype = o.getType()
            if ttype:
                ttype = TTypes.getValue(ttype[0])
            else:
                ttype = ''
            rows.append({'Title': o.Title(),
                         'Type': ttype})

        rows = sorted(rows, cmp=lambda x,y: cmp(x.lower(), y.lower()), key=itemgetter(sidx and sidx or 'Title'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page':page,
               'total':pages,
               'records':len(rows),
               'rows':rows[ (int(page) - 1) * int(nr_rows) : int(page) * int(nr_rows) ]}

        return json.dumps(ret)

class ajaxGetDrugProhibitions(BrowserView):
    """ Drug Prohibition Explanations vocabulary source for jquery combo dropdown box
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = self.request['searchTerm'].lower()
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        rows = []

        # lookup objects from ZODB
        brains = self.bika_setup_catalog(portal_type = 'DrugProhibition')
        if brains and searchTerm:
            brains = [p for p in brains if p.Title.lower().find(searchTerm) > -1]

        for p in brains:
            rows.append({'Title': p.Title})

        rows = sorted(rows, cmp=lambda x,y: cmp(x.lower(), y.lower()), key=itemgetter(sidx and sidx or 'Title'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page':page,
               'total':pages,
               'records':len(rows),
               'rows':rows[ (int(page) - 1) * int(nr_rows) : int(page) * int(nr_rows) ]}

        return json.dumps(ret)

class ajaxGetImmunizations(BrowserView):
    """ Immunizations vocabulary source for jquery combo dropdown box
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = self.request['searchTerm'].lower()
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        rows = []

        # lookup objects from ZODB
        brains = self.bika_setup_catalog(portal_type = 'Immunization')
        if brains and searchTerm:
            brains = [p for p in brains if p.Title.lower().find(searchTerm) > -1]

        for p in brains:
            rows.append({'Title': p.Title})

        rows = sorted(rows, cmp=lambda x,y: cmp(x.lower(), y.lower()), key=itemgetter(sidx and sidx or 'Title'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page':page,
               'total':pages,
               'records':len(rows),
               'rows':rows[ (int(page) - 1) * int(nr_rows) : int(page) * int(nr_rows) ]}

        return json.dumps(ret)

class ajaxGetVaccinationCenters(BrowserView):
    """ Vaccination Centers vocabulary source for jquery combo dropdown box
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = self.request['searchTerm'].lower()
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        rows = []

        # lookup objects from ZODB
        brains = self.bika_setup_catalog(portal_type = 'VaccinationCenter')
        if brains and searchTerm:
            brains = [p for p in brains if p.Title.lower().find(searchTerm) > -1]

        for p in brains:
            rows.append({'Title': p.Title})

        rows = sorted(rows, cmp=lambda x,y: cmp(x.lower(), y.lower()), key=itemgetter(sidx and sidx or 'Title'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page':page,
               'total':pages,
               'records':len(rows),
               'rows':rows[ (int(page) - 1) * int(nr_rows) : int(page) * int(nr_rows) ]}

        return json.dumps(ret)

class ajaxGetSymptoms(BrowserView):
    """ Symptoms from ICD and Site Setup
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = self.request['searchTerm'].lower()
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        rows = []

        # lookup objects from ZODB
        brains = self.bika_setup_catalog(portal_type = 'Symptom')
        if brains and searchTerm:
            brains = [p for p in brains if p.Title.lower().find(searchTerm) > -1
                                        or p.Description.lower().find(searchTerm) > -1]
        for p in brains:
            p = p.getObject()
            rows.append({'Code': p.getCode(),
                         'Title': p.Title(),
                         'Description': p.Description()})

        # lookup objects from ICD code list
        for icd9 in icd9_codes['R']:
            if icd9['code'].find(searchTerm) > -1 \
               or icd9['short'].lower().find(searchTerm) > -1 \
               or icd9['long'].lower().find(searchTerm) > -1:
                rows.append({'Code': icd9['code'],
                             'Title': icd9['short'],
                             'Description': icd9['long']})

        rows = sorted(rows, cmp=lambda x,y: cmp(x.lower(), y.lower()), key=itemgetter(sidx and sidx or 'Title'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page':page,
               'total':pages,
               'records':len(rows),
               'rows':rows[ (int(page) - 1) * int(nr_rows) : int(page) * int(nr_rows) ]}

        return json.dumps(ret)

class ajaxGetIdentifierTypes(BrowserView):
    """ Identifier types vocabulary source for jquery combo dropdown box
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = self.request['searchTerm'].lower()
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        rows = []

        # lookup objects from ZODB
        brains = self.bika_setup_catalog(portal_type = 'IdentifierType')
        if brains and searchTerm:
            brains = [p for p in brains if p.Title.lower().find(searchTerm) > -1]

        for p in brains:
            rows.append({'Title': p.Title,
                         'Description':p.Description,
                         'UID':p.UID})

        rows = sorted(rows, cmp=lambda x,y: cmp(x.lower(), y.lower()), key=itemgetter(sidx and sidx or 'Title'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page':page,
               'total':pages,
               'records':len(rows),
               'rows':rows[ (int(page) - 1) * int(nr_rows) : int(page) * int(nr_rows) ]}

        return json.dumps(ret)
