from Products.CMFCore.utils import getToolByName
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _
from zope.interface import implements, alsoProvides
from bika.lims.utils import logged_in_client
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IContentsPage

class FolderListingView(BikaListingView):
    """Show a list of existing reports
    """
    # IContentsPage hides the "Actions" and "Display" menus
    implements(IViewView)

    def __init__(self, context, request):
        super(FolderListingView, self).__init__(context, request)
        alsoProvides(request, IContentsPage)

        # this will be reset in the call to filter on own reports
        self.contentFilter = {
            'portal_type': 'ReportCollection',
            'sort_on': 'created',
            'sort_order': 'reverse'}

        self.columns = {
            'Client': {'title': _('Client')},
            'Title': {'title': _('Title')},
            'Type': {'title': _('Report Type')},
            'FileSize': {'title': _('Size')},
            'Created': {'title': _('Created')},
            'By': {'title': _('By')},
        }
        self.review_states = [
            {'id': 'default',
             'title': 'All',
             'contentFilter': {},
             'columns': ['Client',
                         'Title',
                         'Type',
                         'FileSize',
                         'Created',
                         'By']},
        ]

        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.icon = self.portal_url + "/++resource++bika.lims.images/report_big.png"
        self.title = self.context.translate(_("Reports"))
        self.description = ""

    def __call__(self):
        this_client = logged_in_client(self.context)
        if this_client:
            self.contentFilter['ClientUID'] = this_client.UID()
            del(self.columns['Client'])
            for x in len(self.review_states):
                del(self.review_states[x]['columns']['Client'])

        return super(FolderListingView, self).__call__()

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        props = self.context.portal_properties.site_properties
        for x in range(len(items)):
            if 'obj' not in items[x]:
                continue
            obj = items[x]['obj']

            items[x]['Type'] = obj.getReportType()
            items[x]['Created'] = self.ulocalized_time(obj.created())
            items[x]['By'] = self.user_fullname(obj.Creator())

            PDF = obj.getPDF()
            if PDF:
                items[x]['FileSize'] = '%sKb' % (PDF.get_size() / 1024)
                items[x]['replace']['Title'] = \
                    "<a href='%s/at_download/ReportFile'>%s</a>" % \
                    (obj.absolute_url(), items[x]['Title'])
            else:
                items[x]['FileSize'] = ''

            client = obj.getClient()
            if client:
                items[x]['replace']['Client'] = \
                    "<a href='%s'>%s</a>" % \
                    (client.absolute_url(), client.Title())
            else:
                items[x]['Client'] = ''
        return items
