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
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IContacts
from bika.lims.permissions import *
from bika.lims.subscribers import doActionFor, skip
from bika.lims.utils import isActive
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
                    'url':PR.absolute_url()+'/ar_add',
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

    template = ViewPageTemplateFile("templates/treatmenthistory.pt")

    def __call__(self):
        if 'submitted' in self.request:
            bsc = self.bika_setup_catalog
            new = []
            for t in range(len(self.request.form['Treatment'])):
                T = self.request.form['Treatment'][t]
                D = self.request.form['Drug'][t]
                S = self.request.form['Start'][t]
                E = self.request.form['End'][t]
                # Create new Treatment entry if none exists
                Tlist = bsc(portal_type='Treatment', Title=T)
                if not Tlist:
                    folder = self.context.bika_setup.bika_treatments
                    _id = folder.invokeFactory('Treatment', id = 'tmp')
                    obj = folder[_id]
                    obj.edit(title = T)
                    obj.unmarkCreationFlag()
                    renameAfterCreation(obj)
                # Create new Drug entry if none exists
                Dlist = bsc(portal_type='Drug', Title=D)
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

class AllergiesView(BrowserView):
    """ bika listing to display Allergies for Drug Prohibitions
    """

    template = ViewPageTemplateFile("templates/allergies.pt")

    def __call__(self):
        if 'submitted' in self.request:
            bsc = self.bika_setup_catalog
            new = []
            for p in range(len(self.request.form['DrugProhibition'])):
                P = self.request.form['DrugProhibition'][p]
                D = self.request.form['Drug'][p]

                # Create new Allergy entry if none exists
                Plist = bsc(portal_type='DrugProhibition', Title=P)
                if not Plist:
                    folder = self.context.bika_setup.bika_drugprohibitions
                    _id = folder.invokeFactory('DrugProhibition', id = 'tmp')
                    obj = folder[_id]
                    obj.edit(title = P)
                    obj.unmarkCreationFlag()
                    renameAfterCreation(obj)
                # Create new Drug entry if none exists
                Dlist = bsc(portal_type='Drug', Title=D)
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

class ImmunizationHistoryView(BrowserView):
    """ bika listing to display Immunization history
    """

    template = ViewPageTemplateFile("templates/immunizationhistory.pt")

    def __call__(self):
        if 'submitted' in self.request:
            bsc = self.bika_setup_catalog
            new = []
            for i in range(len(self.request.form['Immunization'])):
                I = self.request.form['Immunization'][i]
                V = self.request.form['VaccinationCenter'][i]
                D = self.request.form['Date'][i]
                                    
                # Create new VaccinationCenter entry if none exists
                Vlist = bsc(portal_type='VaccinationCenter', Title=V)
                if not Vlist:
                    folder = self.context.bika_setup.bika_vaccinationcenters
                    _id = folder.invokeFactory('VaccinationCenter', id='tmp')
                    obj = folder[_id]
                    obj.edit(title = V)
                    obj.unmarkCreationFlag()
                    renameAfterCreation(obj)
                
                new.append({'Immunization':I, 'VaccinationCenter':V, 'Date':D})
                
            self.context.setImmunizationHistory(new)
            self.context.plone_utils.addPortalMessage(PMF("Changes saved"))
        return self.template()
    
    def getEPINumber(self):
        return "cac";

class ajaxGetPatients(BrowserView):
    """ Patient vocabulary source for jquery combo dropdown box
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = self.request['searchTerm']
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        wf = getToolByName(self.context, 'portal_workflow')
        rows = []

        if searchTerm and len(searchTerm) < 3:
            return json.dumps(rows)

        # lookup patient objects from ZODB
        aq = MatchRegexp('Title', "%s" % searchTerm) | \
             MatchRegexp('Description', "%s" % searchTerm) | \
             MatchRegexp('getPatientID', "%s" % searchTerm)
        brains = self.bika_patient_catalog.evalAdvancedQuery(aq)

        for patient in (o.getObject() for o in brains):
            rows.append({'Title': patient.Title() or '',
                         'PatientID': patient.getPatientID(),
                         'PrimaryReferrer': patient.getPrimaryReferrer().Title(),
                         'PatientUID': patient.UID()})

        rows = sorted(rows, key=itemgetter(sidx and sidx or 'Title'))
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
        searchTerm = self.request['searchTerm']
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

        rows = sorted(rows, key=itemgetter(sidx and sidx or 'Title'))
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
        searchTerm = self.request['searchTerm']
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        rows = []

        # lookup objects from ZODB
        brains = self.bika_setup_catalog(portal_type = 'Treatment')
        if brains and searchTerm:
            brains = [p for p in brains if p.Title.lower().find(searchTerm) > -1]

        for p in brains:
            rows.append({'Title': p.Title})

        rows = sorted(rows, key=itemgetter(sidx and sidx or 'Title'))
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
        searchTerm = self.request['searchTerm']
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

        rows = sorted(rows, key=itemgetter(sidx and sidx or 'Title'))
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
        searchTerm = self.request['searchTerm']
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

        rows = sorted(rows, key=itemgetter(sidx and sidx or 'Title'))
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
        searchTerm = self.request['searchTerm']
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

        rows = sorted(rows, key=itemgetter(sidx and sidx or 'Title'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page':page,
               'total':pages,
               'records':len(rows),
               'rows':rows[ (int(page) - 1) * int(nr_rows) : int(page) * int(nr_rows) ]}

        return json.dumps(ret)