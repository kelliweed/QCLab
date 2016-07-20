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
        storage_levels = self.context.objectValues('StorageLevel')
        storage_locations = self.context.objectValues('StorageLocation')

        # Should not have both levels and locations at one place
        if storage_levels:
            self.title = "Storage Levels in %s" % self.context.title
        elif storage_locations:
            self.title = "Storage Locations in %s" % self.context.title

        self.storagelevels_table = \
            self.get_storagelevels_table(storage_levels)

        self.storagelocations_table = \
            self.get_storagelocations_table(storage_locations)

        return self.template()

    def get_storagelocations_table(self, storage_locations):
        if storage_locations:
            View = StorageLocationsView(self.context, self.request)
            table = View.contents_table(table_only=True)
        else:
            table = ""
        return table

    def get_storagelevels_table(self, storage_levels):
        if storage_levels:
            View = StorageLevelsListingView(self.context, self.request)
            table = View.contents_table(table_only=True)
        else:
            table = ""
        return table

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

        self.icon = self.portal_url + \
                    '/++resource++bika.sanbi.images/storage_big.png'

        self.show_sort_column = False

        self.show_select_row = False

        self.show_select_column = True

        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Title'), 'index': 'sortable_title'},
            'Temperature': {'title': _('Temperature'), 'toggle': True},
            'Department': {'title': _('Department'), 'toggle': False},
            'Address': {'title': _('Address'), 'toggle': False},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['Title',
                         'Temperature',
                         'Department',
                         'Address']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Title',
                         'Temperature',
                         'Department',
                         'Address']},
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

        self.icon = self.portal_url + \
                    '/++resource++bika.sanbi.images/storage_big.png'

        self.show_sort_column = False

        self.show_select_row = False

        self.show_select_column = True

        self.pagesize = 25

        self.columns = {
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
             'columns': ['Title',
                         'StorageTypes',
                         'StoredItem',
                         'review_state']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Title',
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

            items[x]['Title'] = obj.Title()
            items[x]['StorageTypes'] = '<br/>'.join(obj.getStorageTypes())
            si = obj.getStoredItem()
            items[x]['StoredItem'] = si.Title() if si else ''

        return items
