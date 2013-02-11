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
    template = ViewPageTemplateFile("templates/epidemiology_numcasespercountry.pt")

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
            message = _("No cases found")
            self.context.plone_utils.addPortalMessage(message, "error")
            return self.default_template()
                
        groupby = self.request.form.get('GroupingPeriod', '')
        if (groupby != ''):
            parms.append({"title": _("Grouping period"), "value": _(groupby)})
           
        templines = {}
        counts = {'Total':0}
        
        for batch in batches:
            batch = batch.getObject()
            datecreated = batch.created()
            country = batch.getPatientCountry();
            country = country and country or _('Unknown')
            
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
            
            countryline = {"Count": 0 }
            dataline = {}
            if group in templines:
                dataline = templines[group]
                if country in dataline:
                    countryline = dataline[country]                    
            
            countryline["Count"]+=1
            dataline[country] = countryline
            templines[group] = dataline       
                        
            counts["Total"] += 1
            counts[country] = country in counts and counts[country]+1 or 1
            counts[group] = group in counts and counts[group]+1 or 1
        
        datalines = {}
        
        # Percentage calculations
        for period, countries in templines.iteritems():
            for country, values in countries.iteritems():
                countryline = values;                
                countryline['RatioGroup'] = values['Count']/counts[period]
                countryline['RatioTotal'] = values['Count']/counts['Total']
                countryline['PercentageGroup'] = ('{0:.0f}'.format(countryline['RatioGroup']*100))+"%"
                countryline['PercentageTotal'] = ('{0:.0f}'.format(countryline['RatioTotal']*100))+"%"
                if period in datalines:
                    dataline = datalines[period]
                dataline[country] = countryline
                datalines[period] = dataline
        
        self.report_data = {'parameters': parms,
                            'datalines': datalines}
                    
        return {'report_title': _('Number of cases per country'),
                'report_data': self.template()}    
        