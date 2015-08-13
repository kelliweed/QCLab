# -*- coding:utf-8 -*-
from zope.browsermenu.menu import BrowserMenu, BrowserSubMenuItem
from zope.interface import implements

from bika.lims import bikaMessageFactory as _


class ProductivitySubMenuItem(BrowserSubMenuItem):

    submenuId = 'productivity_reports'
    id = submenuId
    order = 3
    title = _('Productivity')
    description = _('Productivity Reports')

    @property
    def extra(self):
        return {'id': 'bika-reports-productivity'}

    @property
    def action(self):
        return '%s/?' % self.context.absolute_url()

    def available(self):
        return True

    def selected(self):
        return False

class ProductivityMenu(BrowserMenu):

    def getMenuItems(self, context, request):
        """Return menu items for consumption by plone/app/contentmenu.pt
        """
        return [
            {'id': x[0],
             'title': x[1],
             'description': x[2],
             'action': 'create_report?report=productivity_' + x[0],
             'selected': False,
             'icon': None,
             'extra': {'separator': None,
                       'id': x[0],
                       'class': 'contenttype-reportcollection'},
             'submenu': None
             } for x in [
                ('dailysamplesreceived',
                 _('Daily samples received'),
                 _('Lists all samples received for a date range')
                 ),
                ('samplesreceivedvsreported',
                 _('Samples received vs. samples reported'),
                 _('Report tables between a period of time the number of '
                   'samples received and results reported for them with '
                   'differences between the two')
                 ),
                ('analysesperservice',
                 _('Analyses per service'),
                 _('The number of analyses requested per analysis service')
                 ),
                ('analysespersampletype',
                 _('Analyses per sample type'),
                 _('The number of analyses requested per sample type')
                 ),
                ('analysesperclient',
                 _('Analysis requests and analyses per client'),
                 _('The number of requests and analyses per client')
                 ),
                ('analysestats',
                 _('Analysis turnaround time'),
                 _('The turnaround times of analyses')
                 ),
                ('analysestats_overtime',
                 _('Analysis turnaround time over time'),
                 _('The turnaround times of analyses plotted over time')
                 ),
                ('analysesperdepartment',
                 _('Analyses summary per department'),
                 _('Number of analysis requested and published per department '
                   'and expresed as a percentage of all analyses performed')
                 ),
                ('analysesperformedpertotal',
                 _('Analyses performed and published as % of total'),
                 _('Report tables between a period of time the number of '
                   'analyses published and expressed as a percentage of all '
                   'analyses performed.')
                 ),
                ('analysesattachments',
                 _('Attachments'),
                 _('The attachments linked to analysis requests and analyses')
                 ),
                ('dataentrydaybook',
                 _('Data entry day book'),
                 _('Report tables of Analysis Requests and totals submitted '
                   'between a period of time')
                 ),
            ]]

class QualityControlSubMenuItem(BrowserSubMenuItem):

    submenuId = 'qualitycontrol_reports'
    id = submenuId
    order = 5
    title = _('Quality Control')
    description = _('Quality Control Reports')

    @property
    def extra(self):
        return {'id': 'bika-reports-qualitycontrol'}

    @property
    def action(self):
        return '%s/?' % self.context.absolute_url()

    def available(self):
        return True

    def selected(self):
        return False

class QualityControlMenu(BrowserMenu):

    def getMenuItems(self, object, request):
        return [
            {'id': x[0],
             'title': x[1],
             'description': x[2],
             'action': 'create_report?report=qualitycontrol_' + x[0],
             'selected': False,
             'icon': None,
             'extra': {'separator': None,
                       'id': x[0],
                       'class': 'contenttype-reportcollection'},
             'submenu': QualityControlSubMenuItem
             } for x in [
                ('analysesoutofrange',
                 _('Analyses out of range'),
                 _('Analysis results out of lab or client specified range. '
                   'Note that this may take several minutes')
                 ),
                ('analysesrepeated',
                 _('Analyses repeated'),
                 _('Repeated analyses')
                 ),
                ('resultspersamplepoint',
                 _('Results per sample point'),
                 _('Results per samplepoint and analysis service')
                 ),
                ('referenceanalysisqc',
                 _('Reference analysis QC'),
                 _('Reference analysis quality control graphs')
                 ),
                ('duplicateanalysisqc',
                 _('Duplicate analysis QC'),
                 _('Duplicate analysis quality control graphs')
                 ),
            ]]


class AdministrationSubMenuItem(BrowserSubMenuItem):
    submenuId = 'administration_reports'
    id = submenuId
    order = 7
    title = _('Administration')
    description = _('Administration Reports')

    @property
    def extra(self):
        return {'id': 'bika-reports-adminstration'}

    @property
    def action(self):
        return '%s/?' % self.context.absolute_url()

    def available(self):
        return True

    def selected(self):
        return False

class AdministrationMenu(BrowserMenu):

    def getMenuItems(self, object, request):
        return [
            {'id': x[0],
             'title': x[1],
             'description': x[2],
             'action': 'create_report?report=administration_' + x[0],
             'selected': False,
             'icon': None,
             'extra': {'separator': None,
                       'id': x[0],
                       'class': 'contenttype-reportcollection'},
             'submenu': None
             } for x in [
                ('arsnotinvoiced',
                 _('Analysis requests not invoiced'),
                 _('Report of published analysis requests which have not '
                   'been invoiced')
                 ),
                ('userhistory',
                 _('User history'),
                 _('Actions performed by users (or specific user) between '
                   'a period of time')
                 )
            ]]
