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
    template = ViewPageTemplateFile("templates/epidemiology_analysisrequestspercountry.pt")

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
                                
        # Query the catalog and store results in a dictionary             
        ars = self.bika_catalog(self.contentFilter)
        if not ars:
            message = _("No analysis requests matched your query")
            self.context.plone_utils.addPortalMessage(message, "error")
            return self.default_template()
        
        arlines = {}
        datalines = {}
        footlines = {}
        
        groupby = ('GroupingPeriod' in self.request.form) and self.request.form['GroupingPeriod'] or 'Day'   
        parms.append({"title": _("Grouping period"), "value": _(groupby)})
             
        for ar in ars:
            
            countryline = {'Country':'',
                           'AnalysisRequests':[]}
            
            arline = {'AnalysisRequestID':'',
                      'PatientID':'',
                      'PatientFirstName':'',
                      'PatientAge':0,
                      'PatientGender':'',
                      'HospitalAnalysisRequestID':'',
                      'SampleType':'',
                      'DateSampled':'',
                      'DateReceived':'',
                      'CaseOnsetDate':'',
                      'AdditionalNotes':'',
                      'ProvisionalDiagnosis':[],
                      'SignsAndSymptoms':[]}
            
            groupline = {'Group':'',
                         'Countries':{}}
            
            
            ar = ar.getObject()       
            arid = ar.getRequestID()  
            datecreated = ar.created()     
            batch = ar.getBatch()       
            country = batch and batch.getPatientCountry() or _("Unknown")
            country = (country and len(country) > 0) and country or _("Unknown")
            countryline['Country'] = country
            arline['AnalysisRequestID'] = arid
            arline['PatientID'] = batch and batch.getPatientID() or ''
            arline['PatientFirstName'] = batch and batch.getPatientFirstname() or ''
            arline['PatientAge'] = (batch and batch.getPatientAgeAtCaseOnsetDate()) and batch.getPatientAgeAtCaseOnsetDate().get('year','') or ''
            arline['PatientGender'] = batch and batch.getPatientGender() or ''
            arline['HospitalAnalysisRequestID'] = ar.getClientSampleID()
            arline['SampleType'] = ar.getSampleTypeTitle()
            arline['DateSampled'] = self.ulocalized_time(ar.getSamplingDate())
            arline['DateReceived'] = self.ulocalized_time(ar.getDateReceived())
            arline['CaseOnsetDate'] = (batch and batch.getOnsetDate()) and self.ulocalized_time(batch.getOnsetDate()) or ''
            arline['AdditionalNotes'] = batch and batch.getAdditionalNotes() or []
            arline['ProvisionalDiagnosis'] = batch and batch.getProvisionalDiagnosis() or []
            arline['SignsAndSymptoms'] = batch and batch.getSymptoms() or []
            
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
                                
            if arid in arlines:
                arline = arlines[arid]                       
            
            countryline['AnalysisRequests'].append(arid)
            groupline['Countries'][country]=countryline
            arlines[arid] = arline            
            datalines[group] = groupline
            
        self.report_data = {'parameters': parms,
                            'datalines': datalines,
                            'analysisrequests': arlines}
                    
        return {'report_title': _('Analysis Requests per country'),
                'report_data': self.template()}    
        