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
    template = ViewPageTemplateFile("templates/epidemiology_resultspercountry.pt")

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
                                                    'getOnsetDate',
                                                    _('Onset Date')) 
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
        batches = self.bika_catalog(self.contentFilter)
        if not batches:
            message = _("No cases found")
            self.context.plone_utils.addPortalMessage(message, "error")
            return self.default_template()
        
        resultkeys = []
        datalines = {}
        footlines = {'Total':{'Results':{},
                            'NumAnalyses':0,
                            'NumCases':0,
                            'NumARs':0,
                            'NumSamples':0,
                            'NumPatients':0}}
        
        groupby = self.request.form.get('GroupingPeriod', '')
        if (groupby != ''):
            parms.append({"title": _("Grouping period"), "value": _(groupby)})
        
        for batch in batches:
            batch = batch.getObject()
            datecreated = batch.created()
            onsetdate = batch.getOnsetDate()
            caseid = batch.getBatchID()
            patientid = batch.getPatientID()
            country = batch.getPatientCountryText()

            group = ''
            if onsetdate is None:
                group = _("Unknown")
            elif groupby == 'Day':
                group = self.ulocalized_time(onsetdate)                 
            elif groupby == 'Week':
                group = onsetdate.strftime("%Y") + ", " + onsetdate.strftime("%U")                                
            elif groupby == 'Month':
                group = onsetdate.strftime("%B") + " " + onsetdate.strftime("%Y")            
            elif groupby == 'Year':
                group = onsetdate.strftime("%Y")
            else:
                group = ''
            
            countryline = {'Country': country,
                           'Results':{},
                           'Analyses':[],
                           'Patients':[],
                           'Cases':[],
                           'ARs':[],
                           'Samples':[] }
            
            dataline = {country:countryline}  
            if group in datalines:
                dataline = datalines[group]            
            if country in dataline:
                countryline = dataline[country]
            
            casefound = False       
            ars = batch.getAnalysisRequests()
            for ar in ars:                
                arid = ar.getId()    
                sample = ar.getSample().getSampleID()     
                analyses = ar.getAnalyses()
                for an in analyses:
                    an = an.getObject()
                    anuid = an.UID()
                    if (an.getServiceUID() == service_uid): 
                        casefound = True
                        if patientid not in countryline['Patients']:
                            countryline['Patients'].append(patientid)
                        if caseid not in countryline['Cases']:
                            countryline['Cases'].append(caseid)
                        if arid not in countryline['ARs']:
                            countryline['ARs'].append(arid)
                        if sample not in countryline['Samples']:
                            countryline['Samples'].append(sample)
                        if anuid not in countryline['Analyses']:
                            countryline['Analyses'].append(anuid)

                        result = an.getResultText()

                        if result not in resultkeys:
                            resultkeys.append(result)

                        countryline['Results'][result] = result in countryline['Results'].keys() and countryline['Results'][result]+1 or 1      

                        if group not in footlines:
                            footlines[group] = {'Results':{},
                                                'NumAnalyses':0,
                                                'NumCases':0,
                                                'NumARs':0,
                                                'NumSamples':0,
                                                'NumPatients':0}                        
                        footlines[group]['Results'][result] = result in footlines[group]['Results'].keys() and footlines[group]['Results'][result]+1 or 1    
                        footlines['Total']['Results'][result] = result in footlines['Total']['Results'].keys() and footlines['Total']['Results'][result]+1 or 1        
                        
            if casefound:
                countryline['NumAnalyses'] = len(countryline['Analyses'])
                countryline['NumCases'] = len(countryline['Cases'])
                countryline['NumARs'] = len(countryline['ARs'])
                countryline['NumSamples'] = len(countryline['Samples'])
                countryline['NumPatients'] = len(countryline['Patients'])                
                
                footlines[group]['NumAnalyses'] += countryline['NumAnalyses']
                footlines[group]['NumCases'] += countryline['NumCases']
                footlines[group]['NumARs'] += countryline['NumARs']
                footlines[group]['NumSamples'] += countryline['NumSamples']
                footlines[group]['NumPatients'] += countryline['NumPatients']
                
                footlines['Total']['NumAnalyses'] += countryline['NumAnalyses']
                footlines['Total']['NumCases'] += countryline['NumCases']
                footlines['Total']['NumARs'] += countryline['NumARs']
                footlines['Total']['NumSamples'] += countryline['NumSamples']
                footlines['Total']['NumPatients'] += countryline['NumPatients']
                
                dataline[country] = countryline
                datalines[group] = dataline 
                
        if len(datalines) == 0:
            message = _("No analyses found")
            self.context.plone_utils.addPortalMessage(message, 'error')
            return self.default_template()
                
        self.report_data = {'parameters': parms,
                            'resultkeys':resultkeys,
                            'datalines': datalines,
                            'footlines':footlines}
                    
        return {'report_title': _('Results summary per country'),
                'report_data': self.template()}    
        