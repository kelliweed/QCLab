from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.reports.selection_macros import SelectionMacrosView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

class Report(BrowserView):
    implements(IViewView)
    default_template = ViewPageTemplateFile("templates/epidemiology.pt")
    template = ViewPageTemplateFile("templates/epidemiology_casespercountry.pt")

    def __init__(self, context, request, report=None):
        super(Report, self).__init__(context, request)
        self.report = report
        self.selection_macros = SelectionMacrosView(self.context, self.request)

    def __call__(self):
        
        parms = []
        titles = []
        
        # Apply filters
        self.contentFilter = {'portal_type': 'Batch'}
        val = self.selection_macros.parse_daterange(self.request,
                                                    'getDateCreated',
                                                    _('Date Created')) 
        if val:
            self.contentFilter[val['contentFilter'][0]] = val['contentFilter'][1]
            parms.append(val['parms'])
            titles.append(val['titles'])           
                                
        # Query the catalog and store results in a dictionary             
        batches = self.bika_catalog(self.contentFilter)
        if not batches:
            message = _("No batches matched your query")
            self.context.plone_utils.addPortalMessage(message, "error")
            return self.default_template()
        
        batchlines = {}
        datalines = {}
        footlines = {}
        
        groupby = ('GroupingPeriod' in self.request.form) and self.request.form['GroupingPeriod'] or 'Day'        
        for batch in batches:
            
            countryline = {'Country':'',
                           'Batches':[]}
            
            batchline = {'BatchID':'',
                         'ClientBatchID':'',
                         'DateCreated':'',
                         'OnsetDate':'',
                         'PatientAge':0,
                         'PatientGender':'',
                         'PatientCountry':'',
                         'NumAnalyses':0,
                         'Analyses': {}}
            
            groupline = {'Group':'',
                         'Countries':{}}
            
            
            batch = batch.getObject()       
            batchid = batch.getBatchID()     
            datecreated = batch.created()
            country = batch.getPatientCountry()
            countryline['Country'] = country;
            batchline['BatchID'] = batchid;
            batchline['ClientBatchID'] = batch.getClientBatchID()
            batchline['OnsetDate'] = self.ulocalized_time(batch.getOnsetDate())
            batchline['PatientAge'] = batch.getPatientAgeAtCaseOnsetDate()['year']
            batchline['PatientGender'] = batch.getPatientGender()
            batchline['PatientCountry'] = country
            batchline['DateCreated'] = datecreated
            
            group = ''
            if groupby == 'Day':
                group = self.ulocalized_time(datecreated)                 
            elif groupby == 'Week':
                group = datecreated.strftime("%Y") + ", " + datecreated.strftime("%U")                                
            elif groupby == 'Month':
                group = datecreated.strftime("%B") + " " + datecreated.strftime("%Y")            
            elif groupby == 'Year':
                group = datecreated.strftime("%Y")
            else :
                group = self.ulocalized_time(datecreated)
            
            groupline['Group'] = group
            if group in datalines:
                groupline = datalines[group]
                if country in groupline['Countries']:
                    countryline = groupline['Countries'][country]
                                
            if batchid in batches:
                batchline = batches[batchid]
            
            ars = batch.getAnalysisRequests()            
            for ar in ars:
                arid = ar.getRequestID()                
                analyses = ar.getAnalyses()
                batchline['NumAnalyses'] = batchline['NumAnalyses'] + len(analyses)
                for an in analyses:
                    an = an.getObject()
                    keyword = an.getKeyword()
                    anline = {'Keyword': keyword,
                              'AnalysisRequest': arid,
                              'ServiceTitle': an.getServiceTitle(),
                              'Result': an.getResult()}
                    batchline['Analyses'][arid+"."+keyword] = anline
            
            
            countryline['Batches'].append(batchid)
            groupline['Countries'][country]=countryline
            batchlines[batchid] = batchline            
            datalines[group] = groupline
            
        self.report_data = {'parameters': parms,
                            'datalines': datalines,
                            'batches': batchlines}
                    
        return {'report_title': _('Cases summary per country'),
                'report_data': self.template()}    
        