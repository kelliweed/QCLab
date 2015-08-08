from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ReportView(BrowserView):

    """ Report View
    """

    productivity_dailysamplesreceived_template = ViewPageTemplateFile("templates/productivity_dailysamplesreceived.pt")
    template = productivity_dailysamplesreceived_template

    def __init__(self, context, request):
        super(ReportView, self).__init__(context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/report_big.png"
        
    def __call__(self):
        return self.template()
