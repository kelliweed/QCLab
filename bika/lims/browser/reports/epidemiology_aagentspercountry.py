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
    template = ViewPageTemplateFile("templates/epidemiology_aagentspercountry.pt")

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

        aetiologicagent_uid = self.request.form.get('AetiologicAgentUID', '')
        aetiologicagent = self.reference_catalog.lookupObject(aetiologicagent_uid)
        if not aetiologicagent:
            message = _("No aetiologic agent was selected.")
            self.context.plone_utils.addPortalMessage(message, 'error')
            return self.default_template()
        parms.append({"title": _("Aetiologic Agent"), "value": aetiologicagent.Title()})

        # Query the catalog and store results in a dictionary
        batches = self.bika_catalog(self.contentFilter)
        if not batches:
            message = _("No cases found")
            self.context.plone_utils.addPortalMessage(message, "error")
            return self.default_template()

        datalines = {}

        groupby = self.request.form.get('GroupingPeriod', '')
        if (groupby != ''):
            parms.append({"title": _("Grouping period"), "value": _(groupby)})

        digest = {}
        for batch in batches:
            batch = batch.getObject()
            datecreated = batch.created()
            gender = batch.getPatientGenderText()
            countrystate = batch.getPatientCountryState()
            country = _('Unknown')
            state = _('Unknown')
            if countrystate:
                country = countrystate['country']
                country = len(country) > 0 and country or _('Unknown')
                state = countrystate['state']
                state = len(state) > 0 and state or _('Unknown')

            aes = batch.getAetiologicAgents()
            for ae in aes:
                aetitle = ae["Title"]
                if aetitle == aetiologicagent.Title():
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

                    aesubtype = ae["Subtype"]
                    digtoken = group + "." + country + "." + state + "." + aetitle + "." + aesubtype + "." + gender
                    digline = {"AetiologicAgent": aetitle,
                               "Subtype": aesubtype,
                               "Country": country,
                               "State": state,
                               "Gender": gender,
                               "Period": group,
                               "Count": 0 }
                    if (digtoken in digest):
                        digline = digest[digtoken]
                    digline['Count'] += 1
                    digest[digtoken] = digline

        # Fill datalines
        for digline in digest.values():
            dataline = {digline['Period']:{}}
            if digline['Period'] in datalines:
                line = []
                dataline = datalines[digline['Period']]
                if digline["Country"] in dataline:
                    line = dataline[digline["Country"]]
                line.append(digline)
                dataline[digline["Country"]] = line;
                datalines[digline["Period"]] = dataline;
            else:
                datalines[digline['Period']] = {digline['Country']: [digline]}

        if len(datalines) == 0:
            message = _("No cases found for the selected aetiologic agent")
            self.context.plone_utils.addPortalMessage(message, 'error')
            return self.default_template()

        self.report_data = {'parameters': parms,
                            'datalines': datalines}

        return {'report_title': _('Aetiologic agent prevalent species per country'),
                'report_data': self.template()}

