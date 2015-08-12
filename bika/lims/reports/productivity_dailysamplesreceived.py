from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.querystring import queryparser
from zope.component import getUtilitiesFor
from plone.app.querystring.interfaces import IParsedQueryIndexModifier
from plone.app.contentlisting.interfaces import IContentListing
from Products.CMFCore.utils import getToolByName
from bika.lims.utils import logged_in_client

class Report(BrowserView):

    template = ViewPageTemplateFile(
        "templates/productivity_dailysamplesreceived.pt")

    def __init__(self, context, request={}):
        self.context = context
        self.request = request if request else context.REQUEST

    def __call__(self):
        #
        # We want to check if report data has been created, by verifying
        # that there is content in self.context.getPDF(), getCSV() or getHTML()
        #
        # If there is no content, then we will re-create it with the code
        # that we modify from original reports.
        '''
        commented for testing need to uncomment after done
        html = self.context.getHTML()
        if not html:'''
        return self.create_report()
        '''
        else:
            return html
'''



    def create_report(self):
        #This code comes from the original reports.
        #
        #  To create the HTML, first we will setup variables on self,
        #  like self.report_data.
        #
        #  Then we will call something like:
        
        parms = []
        titles = []

        #results = self.portal_catalog(self.contentFilter)
        sort_on = None
        sort_order = None
        b_start = 0
        b_size = 30
        limit = 0
        self.context.query += self.context.base_query
        parsedquery = queryparser.parseFormquery(
            self.context, self.context.query, sort_on, sort_order)
        index_modifiers = getUtilitiesFor(IParsedQueryIndexModifier)
        for name, modifier in index_modifiers:
            if name in parsedquery:
                new_name, query = modifier(parsedquery[name])
                parsedquery[name] = query
                # if a new index name has been returned, we need to replace
                # the native ones
                if name != new_name:
                    del parsedquery[name]
                    parsedquery[new_name] = query

        # Check for valid indexes
        catalog = getToolByName(self.context, 'portal_catalog')
        valid_indexes = [index for index in parsedquery
                         if index in catalog.indexes()]

        # We'll ignore any invalid index, but will return an empty set if none
        # of the indexes are valid.
        if not valid_indexes:
            logger.warning(
                "Using empty query because there are no valid indexes used.")
            parsedquery = {}

        client = logged_in_client(self.context)
        if client: 
            parsedquery['path'] = {'query': '/'.join(client.getPhysicalPath()), "level": 0}
        #if 'path' not in parsedquery:
        #    parsedquery['path'] = {"query": "/".join(self.context.getPhysicalPath()), "level": 0}

        results = catalog(**parsedquery)
        if getattr(results, 'actual_result_count', False) and limit\
                and results.actual_result_count > limit:
            results.actual_result_count = limit

        self.report_data = {
             'parameters': parms
        }
        import pdb
        pdb.set_trace()
        html = self.template()
        self.context.setHTML(html)
        return html

        #
        # ANd we can generate the PDF from that html, too.
        #
        #
        #  The CSV stuff is handled separate.
        #
        #
        # parms = []
        # titles = []
        # self.contentFilter = {'portal_type': 'Sample',
        #                       'review_state': ['sample_received', 'expired',
        #                                        'disposed'],
        #                       'sort_on': 'DateReceived'}
        #
        # if val:
        #     self.contentFilter[val['contentFilter'][0]] = val['contentFilter'][1]
        #     parms.append(val['parms'])
        #     titles.append(val['titles'])
        #
        # # Query the catalog and store results in a dictionary
        # samples = self.portal_catalog(self.contentFilter)
        # if not samples:
        #     message = _("No samples matched your query")
        #     self.context.plone_utils.addPortalMessage(message, "error")
        #     return self.default_template()
        #
        # datalines = []
        # analyses_count = 0
        # for sample in samples:
        #     sample = sample.getObject()
        #
        #     # For each sample, retrieve the analyses and generate
        #     # a data line for each one
        #     analyses = sample.getAnalyses({})
        #     for analysis in analyses:
        #         analysis = analysis.getObject()
        #         dataline = {'AnalysisKeyword': analysis.getKeyword(),
        #                     'AnalysisTitle': analysis.getServiceTitle(),
        #                     'SampleID': sample.getSampleID(),
        #                     'SampleType': sample.getSampleType().Title(),
        #                     'SampleDateReceived': self.ulocalized_time(
        #                         sample.getDateReceived(), long_format=1),
        #                     'SampleSamplingDate': self.ulocalized_time(
        #                         sample.getSamplingDate(), long_format=1)}
        #         datalines.append(dataline)
        #         analyses_count += 1
        #
        # # Footer total data
        # footlines = []
        # footline = {'TotalCount': analyses_count}
        # footlines.append(footline)
        #
        # self.report_data = {
        #     'parameters': parms,
        #     'datalines': datalines,
        #     'footlines': footlines}
        #
        # if self.request.get('output_format', '') == 'CSV':
        #     import csv
        #     import StringIO
        #     import datetime
        #
        #     fieldnames = [
        #         'SampleID',
        #         'SampleType',
        #         'SampleSamplingDate',
        #         'SampleDateReceived',
        #         'AnalysisTitle',
        #         'AnalysisKeyword',
        #     ]
        #     output = StringIO.StringIO()
        #     dw = csv.DictWriter(output, fieldnames=fieldnames)
        #     dw.writerow(dict((fn, fn) for fn in fieldnames))
        #     for row in datalines:
        #         dw.writerow(row)
        #     report_data = output.getvalue()
        #     output.close()
        #     date = datetime.datetime.now().strftime("%Y%m%d%H%M")
        #     setheader = self.request.RESPONSE.setHeader
        #     setheader('Content-Type', 'text/csv')
        #     setheader("Content-Disposition",
        #               "attachment;filename=\"dailysamplesreceived_%s.csv\"" % date)
        #     self.request.RESPONSE.write(report_data)
        # else:
        #     return {'report_title': _('Daily samples received'),
        #             'report_data': self.template()}
