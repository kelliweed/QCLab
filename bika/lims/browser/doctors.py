from bika.lims.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.client import ClientContactsView
from operator import itemgetter
from bika.lims.permissions import *
import plone
import json

class DoctorsView(ClientContactsView):

    def __init__(self, context, request):
        super(DoctorsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Doctor',
                              'sort_on': 'sortable_title'}
        self.context_actions = {}
        self.title = _("Doctors")
        self.icon = "++resource++bika.lims.images/doctor_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 50

        self.columns = {
            'getDoctorID': {'title': _('Doctor ID')},
            'getFullname': {'title': _('Full Name'),
                            'index': 'getFullname'},
            'getEmailAddress': {'title': _('Email Address')},
            'getBusinessPhone': {'title': _('Business Phone')},
            'getMobilePhone': {'title': _('Mobile Phone')},
        }

        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions':[{'id':'empty'}],
             'columns': ['getDoctorID',
                         'getFullname',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(AddDoctor, self.context):
            self.context_actions[_('Add')] = {
                'url': 'createObject?type_name=Doctor',
                'icon': '++resource++bika.lims.images/add.png'
            }
        if mtool.checkPermission(ManageDoctors, self.context):
            self.show_select_column = True
            self.review_states = [
                {'id':'default',
                 'title': _('All'),
                 'contentFilter':{},
                 'transitions':[{'id':'empty'}],
                 'columns': ['getDoctorID',
                             'getFullname',
                             'getEmailAddress',
                             'getBusinessPhone',
                             'getMobilePhone']},
                {'id':'active',
                 'title': _('Active'),
                 'contentFilter': {'inactive_state': 'active'},
                 'transitions': [{'id':'deactivate'}, ],
                 'columns': ['getDoctorID',
                             'getFullname',
                             'getEmailAddress',
                             'getBusinessPhone',
                             'getMobilePhone']},
                {'id':'inactive',
                 'title': _('Dormant'),
                 'contentFilter': {'inactive_state': 'inactive'},
                 'transitions': [{'id':'activate'}, ],
                 'columns': ['getDoctorID',
                             'getFullname',
                             'getEmailAddress',
                             'getBusinessPhone',
                             'getMobilePhone']},
                ]
        return super(DoctorsView, self).__call__()

    def folderitems(self):
        items = super(DoctorsView, self).folderitems()
        for x in range(len(items)):
            if not 'obj' in items[x]:
                continue
            obj = items[x]['obj']
            items[x]['replace']['getDoctorID'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getDoctorID'])
            items[x]['replace']['getFullname'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getFullname'])

        return items

class ajaxGetDoctors(BrowserView):
    """ vocabulary source for jquery combo dropdown box
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = self.request['searchTerm'].lower()
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']

        rows = []

        pc = self.portal_catalog
        proxies = pc(portal_type="Doctor")
        for doctor in proxies:
            doctor = doctor.getObject()
            if self.portal_workflow.getInfoFor(doctor, 'inactive_state', 'active') == 'inactive':
                continue
            if doctor.Title().lower().find(searchTerm) > -1 \
            or doctor.getDoctorID().lower().find(searchTerm) > -1:
                rows.append({'Title': doctor.Title() or '',
                             'DoctorID': doctor.getDoctorID(),
                             'DoctorUID': doctor.UID()})

        rows = sorted(rows, cmp=lambda x,y: cmp(x.lower(), y.lower()), key = itemgetter(sidx and sidx or 'Title'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page':page,
               'total':pages,
               'records':len(rows),
               'rows':rows[ (int(page)-1)*int(nr_rows) : int(page)*int(nr_rows) ]}

        return json.dumps(ret)
