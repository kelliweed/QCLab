from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IProviders
from plone.app.layout.globals.interfaces import IViewView
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.browser.client import ClientContactsView
from bika.lims.browser.analysisrequest import AnalysisRequestsView
from bika.lims.permissions import *
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

class ProvidersView(ClientContactsView):

    def __init__(self, context, request):
        super(ProvidersView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Provider',
                              'sort_on': 'sortable_title'}
        self.context_actions = {}
        self.title = _("Providers")
        self.icon = "++resource++bika.lims.images/provider_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 50

        self.columns = {
            'getProviderID': {'title': _('Provider ID'),
                              'index': 'getProviderID', },
            'getFullname': {'title': _('Full Name'),
                            'index': 'getFullname'},
            'getProviderRole': {'title': _('Provider Role'),
                                'index': 'getProviderRole',
                                'toggle': True, },
            'getEmailAddress': {'title': _('Email Address')},
            'getBusinessPhone': {'title': _('Business Phone')},
            'getMobilePhone': {'title': _('Mobile Phone')},
        }

        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions':[{'id':'empty'},],
             'columns': ['getProviderID',
                         'getFullname',
                         'getProviderRole',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(AddProvider, self.context):
            self.context_actions[_('Add')] = {
                'url': 'createObject?type_name=Provider',
                'icon': '++resource++bika.lims.images/add.png'
            }
        if mtool.checkPermission(ManageProviders, self.context):
            self.show_select_column = True
            self.review_states = [
                {'id':'default',
                 'title': _('All'),
                 'contentFilter':{},
                 'transitions':[{'id':'empty'},],
                 'columns': ['getProviderID',
                             'getFullname',
                             'getProviderRole',
                             'getEmailAddress',
                             'getBusinessPhone',
                             'getMobilePhone']},
                {'id':'active',
                 'title': _('Active'),
                 'contentFilter': {'inactive_state': 'active'},
                 'transitions': [{'id':'deactivate'}, ],
                 'columns': ['getProviderID',
                             'getFullname',
                             'getProviderRole',
                             'getEmailAddress',
                             'getBusinessPhone',
                             'getMobilePhone']},
                {'id':'inactive',
                 'title': _('Dormant'),
                 'contentFilter': {'inactive_state': 'inactive'},
                 'transitions': [{'id':'activate'}, ],
                 'columns': ['getProviderID',
                             'getFullname',
                             'getProviderRole',
                             'getEmailAddress',
                             'getBusinessPhone',
                             'getMobilePhone']},
                ]
        return super(ProvidersView, self).__call__()

    def folderitems(self):
        items = super(ProvidersView, self).folderitems()
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            del items[x]['replace']['getFullname']
            items[x]['getProviderID'] = obj.getProviderID()
            items[x]['replace']['getProviderID'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getProviderID'])
            items[x]['getProviderRole'] = obj.getProviderRole()

        return items

class ProviderAnalysisRequestsView(AnalysisRequestsView):
    def __init__(self, context, request):
        super(ProviderAnalysisRequestsView, self).__init__(context, request)
        self.contentFilter['getProviderUID'] = self.context.getProviderUID()

schema = ATFolderSchema.copy()
class Providers(ATFolder):
    implements(IProviders)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(Providers, PROJECTNAME)
