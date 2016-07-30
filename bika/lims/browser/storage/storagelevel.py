from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView


class StorageLevelView(BikaListingView):
    """This is the default view for the StorageLevel objects.

    This will show all StorageLevels inside this one
    Or,
    This will show all StorageLocations that this StorageLevel contains.

    A StorageLevel should not contain StorageLocations at the same time as
    containing other StorageLevels.
    """
    template = ViewPageTemplateFile("templates/storagelevel_view.pt")

    def __init__(self, context, request):
        super(StorageLevelView, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        self.levels = self.context.objectValues('StorageLevel')
        self.locations = self.context.objectValues('StorageLocation')

        # Should not have both levels and locations at one place
        if self.levels:
            self.title = "Storages in %s" % self.context.title
            self.icon = self.portal_url + "/++resource++bika.lims.images/" \
                        + "storagelevel_big.png"
            View = StorageLevelsListingView(self.context, self.request)
            self.contents_table = View.contents_table(table_only=True)
        elif self.locations:
            self.title = "Storage positions in %s" % self.context.title
            self.icon = self.portal_url + "/++resource++bika.lims.images/" \
                        + "storagelocation_big.png"
            View = StorageLocationsView(self.context, self.request)
            self.contents_table = View.contents_table(table_only=True)

        return self.template()

class StorageLevelsListingView(BikaListingView):
    """This is the listing that shows StorageLevels at this location.
    It's activated if there are already any storagelevels located here.
    """

    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(StorageLevelsListingView, self).__init__(context, request)

        self.context = context
        self.request = request
        self.catalog = 'bika_setup_catalog'
        path = '/'.join(context.getPhysicalPath())
        self.contentFilter = {'portal_type': 'StorageLevel',
                              'sort_on': 'sortable_title',
                              'path': {'query': path, 'depth': 1, 'level': 0}
                              }
        self.context_actions = {}
        self.title = ''
        self.description = ''
        self.icon = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.columns = {
            'Title': {'title': _('Title'), 'index': 'sortable_title'},
            'Temperature': {'title': _('Temperature'), 'toggle': True},
            'Department': {'title': _('Department'), 'toggle': False},
            'Address': {'title': _('Address'), 'toggle': False},
            'StorageTypes': {'title': _('Storage Types'), 'toggle': True},
            'review_state': {'title': _('State'), 'toggle': True},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['Title',
                         'Temperature',
                         'Department',
                         'Address',
                         'StorageTypes',
                         'review_state']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Title',
                         'Temperature',
                         'Department',
                         'StorageTypes',
                         'review_state']},
        ]

    def folderitems(self, full_objects=False):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']

            items[x]['Temperature'] = obj.getTemperature()
            items[x]['Department'] = obj.getDepartmentTitle()
            items[x]['Address'] = obj.getAddress()
            items[x]['replace']['Title'] = \
                "<a href='%s'>%s</a>" % (items[x]['url'], items[x]['Title'])
            stitles = [s['title'] for s in obj.getStorageTypes()]
            items[x]['StorageTypes'] = ','.join(stitles)
        return items


class StorageLocationsView(BikaListingView):
    """This is the listing that shows StorageLevels at this location.
    It's activated if there are already any storagelevels located here.
    """

    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(StorageLocationsView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.catalog = 'bika_setup_catalog'
        path = '/'.join(context.getPhysicalPath())
        self.contentFilter = {'portal_type': 'StorageLocation',
                              'sort_on': 'sortable_title',
                              'path': {'query': path, 'depth': 1, 'level': 0}
                              }
        self.context_actions = {}
        self.title = ''
        self.description = ''
        self.icon = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.columns = {
            'id': {'title': _('ID'), 'index': 'id'},
            'Title': {'title': _('Title'), 'index': 'sortable_title'},
            'StorageTypes': {'title': _('Storage Types'), 'toggle': True},
            'StoredItem': {'title': _('Stored Item'), 'toggle': True},
            'review_state': {'title': _('State'), 'toggle': True},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['id',
                         'Title',
                         'StorageTypes',
                         'StoredItem',
                         'review_state']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['id',
                         'Title',
                         'StorageTypes',
                         'StoredItem',
                         'review_state']},
        ]

    def folderitems(self, full_objects=False):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']

            items[x]['id'] = obj.getId()
            items[x]['Title'] = obj.Title()
            si = obj.getStoredItem()
            items[x]['StoredItem'] = si.Title() if si else ''
            stitles = [s['title'] for s in obj.getStorageTypes()]
            items[x]['StorageTypes'] = ','.join(stitles)

        return items
