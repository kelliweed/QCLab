from bika.lims.browser import BrowserView
from bika.lims.reports.interfaces import *
from plone.app.contentlisting.interfaces import IContentListing
from zope.interface import alsoProvides
from zope.component import getAdapter


class ViewReport(BrowserView):
    """Report View
    Responsible for looking up the 'ReportCollectionView' adapter.
    """

    def __init__(self, context, request):
        super(ViewReport, self).__init__(context, request)
        alsoProvides(IContentListing)

    def __call__(self):
        adapter = getAdapter(self.context, interface=IReportCollectionView)
        return adapter()
