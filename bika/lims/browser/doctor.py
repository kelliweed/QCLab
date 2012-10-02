from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.AdvancedQuery import Or, MatchRegexp, And, Generic
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

class DoctorAnalysisRequestsView(AnalysisRequestsView):
    def __init__(self, context, request):
        super(DoctorAnalysisRequestsView, self).__init__(context, request)
        self.contentFilter['DoctorUID'] = self.context.UID()

class DoctorSamplesView(SamplesView):
    def __init__(self, context, request):
        super(DoctorSamplesView, self).__init__(context, request)
        self.contentFilter['DoctorUID'] = self.context.UID()

class ajaxGetDoctors(BrowserView):
    """ vocabulary source for jquery combo dropdown box
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
        aq = self.portal_catalog.makeAdvancedQuery({})
        AND = And()
        AND.addSubquery(Generic('portal_type', 'Doctor'))
        AND.addSubquery(Generic('inactive_state', 'active'))
        aq &= AND
        OR = Or()
        OR.addSubquery(MatchRegexp('Title', "%s"%searchTerm))
        OR.addSubquery(MatchRegexp('Description', "%s"%searchTerm))
        aq &= OR
        brains = self.portal_catalog.evalAdvancedQuery(aq)

        for obj in (o.getObject() for o in brains):
            rows.append({'DoctorUID': obj.UID(),
                         'Title': obj.Title() or ''})

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
