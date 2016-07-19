from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView


class StorageLevelsView(BikaListingView):
    """This view shows all this lab's storage levels at /storage
    """

    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(StorageLevelsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        path = '/'.join(self.context.getPhysicalPath())
        self.contentFilter = {'portal_type': 'StorageLevel',
                              'sort_on': 'sortable_title',
                              'path': {'query': path, 'depth': 1, 'level':0}
                              }
        self.context_actions = {}
        self.title = context.translate(_('Storage levels in ${level}',
                                         mapping={'level': context.title}))
        self.description = _("List and summarise the storages at this level")
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
            'Hierarchy': {'title': _('Hierarchy'), 'toggle': True},
            'StorageTypes': {'title': _('Storage Types'), 'toggle': True}
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
                         'Hierarchy']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Title',
                         'Temperature',
                         'Department',
                         'Address',
                         'StorageTypes',
                         'Hierarchy']},
        ]

    def folderitems(self):
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
            items[x]['StorageTypes'] = "I[XXX]Storage"

            items[x]['Hierarchy'] = obj.getHierarchy()
        return items
