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
    template = ViewPageTemplateFile("templates/epidemiology_epiddetailspercase.pt")

    def __init__(self, context, request, report=None):
        super(Report, self).__init__(context, request)
        self.report = report
        self.selection_macros = SelectionMacrosView(self.context, self.request)

    def __call__(self):
        
        parms = []
        titles = []
        
        # Apply filters
        self.contentFilter = {'portal_type': 'AnalysisRequest'}
        val = self.selection_macros.parse_daterange(self.request,
                                                    'getDateCreated',
                                                    _('Date Created')) 
        if val:
            self.contentFilter[val['contentFilter'][0]] = val['contentFilter'][1]
            parms.append(val['parms'])
            titles.append(val['titles'])           
        
        service_uid = self.request.form.get('ServiceUID', '')
        service = self.reference_catalog.lookupObject(service_uid)
        if not service:
            message = _("No analysis services were selected.")
            self.context.plone_utils.addPortalMessage(message, 'error')
            return self.default_template()
        parms.append({"title": _("Analysis"), "value": service.Title()})
        
        # Query the catalog and store results in a dictionary             
        ars = self.bika_catalog(self.contentFilter)
        if not ars:
            message = _("No analyses found")
            self.context.plone_utils.addPortalMessage(message, "error")
            return self.default_template()
        
        datalines = {}
        
        groupby = self.request.form.get('GroupingPeriod', '')
        if (groupby != ''):
            parms.append({"title": _("Grouping period"), "value": _(groupby)})
            
        for ar in ars:            
            ar = ar.getObject()
            arid = ar.getRequestID()
            datecreated = ar.created()
            batch = ar.getBatch()
            if batch is None:
                continue
            
            caseid = batch.getBatchID()
            
            analyses = ar.getAnalyses()
            for an in analyses:
                an = an.getObject()
                if (an.getServiceUID() == service_uid):
                    line = {'AnalysisUID': an.UID(),
                            'CaseID': arid,
                            'HospitalAnalysisRequestID': batch.getClientBatchID(),
                            'Hospital': batch.getClientName(),
                            'SampleType': ar.getSampleTypeTitle(), 
                            'Keyword': an.getKeyword(),
                            'ServiceTitle': an.getServiceTitle(),
                            'Result': an.getResult(),
                            'CaseAdditionalNotes': batch.getAdditionalNotes(),
                            'CaseProvisionalDiagnosis': batch.getProvisionalDiagnosis(),
                            'CaseSignsAndSymptoms': batch.getSymptoms()}
                    
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
                        group = ''
                    
                    analyseslines = {an.UID(): line}
                    if group in datalines:
                        analyseslines = datalines[group]
                        analyseslines[an.UID()] = line
                        
                    datalines[group] = analyseslines
            
        if len(datalines) == 0:
            message = _("No analyses found")
            self.context.plone_utils.addPortalMessage(message, 'error')
            return self.default_template()
        
        self.report_data = {'parameters': parms,
                            'datalines': datalines}
                    
        return {'report_title': _('Epid details per cases'),
                'report_data': self.template()}    
        