from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from plone.app.layout.globals.interfaces import IViewView
from bika.lims.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from bika.lims.interfaces import IStorageUnits

class StorageUnitsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(StorageUnitsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'StorageUnit',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=StorageUnit',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_('Storage Units'))
        self.icon = self.portal_url + '/++resource++bika.lims.images/storagelocation_big.png'
        self.description = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Title'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                         'toggle': False},
            'Temperature': {'title': _('Temperature'),
                                    'toggle': True},
            'Department': {'title': _('Department'),
                         'toggle': True},
            'Floor': {'title': _('Floor'),
                           'toggle': True},
            'Address': {'title': _('Address'),
                           'toggle': False},
            'StorageInstructions': {'title': _('Storage Instructions'),
                           'toggle': False},
        }
        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'Description',
                         'Temperature',
                         'Department',
                         'Floor',
                         'Address',
                         'StorageInstructions']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Description',
                         'Temperature',
                         'Department',
                         'Floor',
                         'Address',
                         'StorageInstructions']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Description',
                         'Temperature',
                         'Department',
                         'Floor',
                         'Address',
                         'StorageInstructions']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Temperature'] = obj.getTemperature()
            items[x]['Department'] = obj.getDepartmentTitle()
            items[x]['Floor'] = obj.getFloor()
            items[x]['Address'] = obj.getAddress()
            items[x]['StorageInstructions'] = obj.getStorageInstructions()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
        return items

schema = ATFolderSchema.copy()
class StorageUnits(ATFolder):
    implements(IStorageUnits)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(StorageUnits, PROJECTNAME)
