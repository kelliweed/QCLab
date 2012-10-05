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

class PatientSamplesView(SamplesView):
    def __init__(self, context, request):
        super(PatientSamplesView, self).__init__(context, request)
        self.contentFilter['getPatientUID'] = self.context.UID()

class TreatmentHistoryView(BikaListingView):
    """ bika listing to display Treatment History for a
        TreatmentHistory field.
    """

    def __init__(self, context, request, fieldvalue=[], allow_edit=True):
        BikaListingView.__init__(self, context, request)
        self.context_actions = {}
        self.contentFilter = {'review_state': 'impossible_state'}
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = False
        self.pagesize = 1000
        self.allow_edit = allow_edit

        self.fieldvalue = fieldvalue

        self.columns = {
            'Treatment': {'title': _('Treatment')},
            'Drug': {'title': _('Drug')},
            'Start': {'title': _('Start')},
            'End': {'title': _('End')},
            'Remarks': {'title': _('Remarks')},

        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions': [],
             'columns':['Treatment', 'Drug', 'Start', 'End'],
            },
        ]

    def folderitems(self):
        items = []
        row_id = 0
        for value in self.fieldvalue:
            # this folderitems doesn't subclass from the bika_listing.py
            # so we create items from scratch
            row_id += 1
            item = {
                'obj': self.context,
                'id': row_id,
                'uid': row_id,
                'type_class': 'treatmenthistory',
                'url': self.context.absolute_url(),
                'relative_url': self.context.absolute_url(),
                'view_url': self.context.absolute_url(),
                'Treatment': value['Treatment'],
                'Drug': value['Drug'],
                'Start': value['Start'],
                'End': value['End'],
                'Remarks': value['Remarks'],
                'replace': {},
                'before': {},
                'after': {},
                'choices':{},
                'class': "state-active",
                'state_class': 'state-active',
                'allow_edit': [],
            }
            items.append(item)
        row_id += 1
        item = {
            'obj': self.context,
            'id': row_id,
            'uid': row_id,
            'type_class': 'treatmenthistory',
            'url': self.context.absolute_url(),
            'relative_url': self.context.absolute_url(),
            'view_url': self.context.absolute_url(),
            'Treatment': '',
            'Drug': '',
            'Start': '',
            'End': '',
            'Remarks': '',
            'replace': {},
            'before': {},
            'after': {},
            'choices':{},
            'class': "state-active",
            'state_class': 'state-active',
            'allow_edit': ['Treatment', 'Drug', 'Start', 'End', 'Remarks'],
        }
        items.append(item)

        return items

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
        aq = MatchRegexp('Title', "%s"%searchTerm) | \
             MatchRegexp('Description', "%s"%searchTerm) | \
             MatchRegexp('getPatientID', "%s"%searchTerm)
        brains = self.bika_patient_catalog.evalAdvancedQuery(aq)

        for patient in (o.getObject() for o in brains):
            rows.append({'Title': patient.Title() or '',
                         'PatientID': patient.getPatientID(),
                         'PrimaryReferrer': patient.getPrimaryReferrer().Title(),
                         'PatientUID': patient.UID()})

        rows = sorted(rows, key = itemgetter(sidx and sidx or 'Title'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page':page,
               'total':pages,
               'records':len(rows),
               'rows':rows[ (int(page)-1)*int(nr_rows) : int(page)*int(nr_rows) ]}

        return json.dumps(ret)
