from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView


class StorageUnitsView(BikaListingView):
    """This view shows all this lab's storage units at /storage
    """

    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(StorageUnitsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'StorageUnit',
                              'sort_on': 'sortable_title'}
        self.context_actions = {
            _('Add one new storage unit'): {
                'url': 'createObject?type_name=StorageUnit',
                'icon': '++resource++bika.lims.images/add.png'}}
        self.title = context.translate(_('Storage units'))
        self.description = _("Displays a list of all the storage units in LIMS")
        self.icon = self.portal_url + \
                    '/++resource++bika.sanbi.images/storage_big.png'
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
            'Address': {'title': _('Address'),
                        'toggle': False},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['Title',
                         'Description',
                         'Temperature',
                         'Department',
                         'Address']},
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['Title',
                         'Description',
                         'Temperature',
                         'Department',
                         'Address']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Title',
                         'Description',
                         'Temperature',
                         'Department',
                         'Address']},
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
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])
        return items
