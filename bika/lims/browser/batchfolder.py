from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View
from AccessControl import getSecurityManager
from bika.lims.permissions import AddBatch
from bika.lims.permissions import ManageAnalysisRequests
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IBatchFolder
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from bika.lims.browser import BrowserView
from zope.interface import implements
from Products.CMFCore import permissions
import plone
import json


class BatchFolderContentsView(BikaListingView):

    implements(IFolderContentsView)

    def __init__(self, context, request):
        super(BatchFolderContentsView, self).__init__(context, request)
        self.catalog = 'bika_catalog'
        self.contentFilter = {'portal_type': 'Batch'}
        self.context_actions = {}
        self.icon = self.portal_url + "/++resource++bika.lims.images/batch_big.png"
        self.title = _("Batches")
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'BatchID': {'title': _('Batch ID')},
            'OnsetDate': {'title': _('Onset Date')},
            'Patient': {'title': _('Patient')},
            'Doctor': {'title': _('Doctor')},
            'Client': {'title': _('Client')},
            'state_title': {'title': _('State'), 'sortable': False},
        }

        self.review_states = [  # leave these titles and ids alone
            {'id':'default',
             'contentFilter': {'cancellation_state':'active',
                               'review_state': ['open', 'sample_received', 'to_be_verified', 'verified']},
             'title': _('Open'),
             'columns':['BatchID',
                        'Patient',
                        'Doctor',
                        'Client',
                        'OnsetDate',
                        'state_title', ]
             },
            {'id':'closed',
             'contentFilter': {'review_state': 'closed'},
             'title': _('Closed'),
             'columns':['BatchID',
                        'Patient',
                        'Doctor',
                        'Client',
                        'OnsetDate',
                        'state_title', ]
             },
            {'id':'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'cancellation_state': 'cancelled'},
             'columns':['BatchID',
                        'Patient',
                        'Doctor',
                        'Client',
                        'OnsetDate',
                        'state_title', ]
             },
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns':['BatchID',
                        'Patient',
                        'Doctor',
                        'Client',
                        'OnsetDate',
                        'state_title', ]
             },
        ]

    def __call__(self):
        if self.context.absolute_url() == self.portal.batches.absolute_url():
            # in contexts other than /batches, we do want to show the edit border
            self.request.set('disable_border', 1)
        if self.context.absolute_url() == self.portal.batches.absolute_url() \
                and self.portal_membership.checkPermission(AddBatch, self.portal.batches):
            self.context_actions[_('Add')] = \
                {'url': 'createObject?type_name=Batch',
                 'icon': self.portal.absolute_url() + '/++resource++bika.lims.images/add.png'}
        if self.context.portal_type == "Client" \
                and self.portal_membership.checkPermission(AddBatch, self.portal.batches):
            clientid = self.context.getClientID()
            url = self.portal.batches.absolute_url() + "/portal_factory/Batch/new/edit?ClientID=%s" % clientid
            self.context_actions[_('Add')] = \
                {'url': url,
                 'icon': self.portal.absolute_url() + '/++resource++bika.lims.images/add.png'}
        return super(BatchFolderContentsView, self).__call__()

    def folderitems(self):
        self.filter_indexes = None

        uc = getToolByName(self.context, 'uid_catalog')

        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if 'obj' not in items[x]:
                items[x]['OnsetDate'] = 'zzz'
                items[x]['replace']['OnsetDate'] = ''
                continue
            obj = items[x]['obj']

            bid = obj.getBatchID()
            items[x]['BatchID'] = bid
            items[x]['replace']['BatchID'] = "<a href='%s'>%s</a>" % (items[x]['url'], bid)

            patient = uc(UID=obj.getPatientUID())
            if patient:
                patient = patient[0].getObject()
                items[x]['Patient'] = patient.Title()
                items[x]['replace']['Patient'] = "<a href='%s'>%s</a>" % (patient.absolute_url(), patient.Title())
            else:
                items[x]['Patient'] = ''

            doctor = uc(UID=obj.getDoctorUID())
            if doctor:
                doctor = doctor[0].getObject()
                items[x]['Doctor'] = doctor.Title()
                items[x]['replace']['Doctor'] = "<a href='%s'>%s</a>" % (doctor.absolute_url(), doctor.Title())
            else:
                items[x]['Doctor'] = ''

            client = uc(UID=obj.getClientUID())
            if client:
                client = client[0].getObject()
                items[x]['Client'] = client.Title()
                items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % (client.absolute_url(), client.Title())
            else:
                items[x]['Client'] = ''

            osd = obj.getOnsetDate()
            if osd:
                items[x]['OnsetDate'] = osd
                items[x]['replace']['OnsetDate'] = self.ulocalized_time(osd)
            else:
                items[x]['OnsetDate'] = 'zzz'
                items[x]['replace']['OnsetDate'] = ''

        items = sorted(items, key = itemgetter('OnsetDate'))
        items.reverse()

        return items


class ajaxGetBatches(BrowserView):
    """ Vocabulary source for jquery combo dropdown box
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        PatientUID = self.request.get('PatientUID', '')
        ClientUID = self.request.get('ClientUID', '')
        searchTerm = 'searchTerm' in self.request and self.request['searchTerm'].lower() or ''
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']

        uc = getToolByName(self.context, 'uid_catalog')

        rows = []

        if PatientUID:
            batches = self.bika_catalog(portal_type='Batch',
                                        getPatientUID=PatientUID,
                                        cancellation_state = 'active')
        elif ClientUID:
            batches = self.bika_catalog(portal_type='Batch',
                                        getClientUID=ClientUID,
                                        cancellation_state = 'active')
        else:
            batches = self.bika_catalog(portal_type='Batch')

        for batch in batches:
            batch = batch.getObject()
            if self.portal_workflow.getInfoFor(batch, 'review_state', 'open') == 'closed':
                continue
            if batch.Title().lower().find(searchTerm) > -1 \
            or batch.Description().lower().find(searchTerm) > -1:

                p_uid = batch.getPatientUID()
                d_uid = batch.getDoctorUID()
                c_uid = batch.getClientUID()

                rows.append({'BatchID': batch.getBatchID(),
                             'BatchUID': batch.UID(),
                             'PatientID': batch.getPatientID(),
                             'PatientTitle': p_uid and uc(UID=p_uid)[0].Title or '',
                             'DoctorID': batch.getDoctorID(),
                             'DoctorTitle': d_uid and uc(UID=d_uid)[0].Title or '',
                             'ClientID': batch.getClientID(),
                             'ClientTitle': c_uid and uc(UID=c_uid)[0].Title or ''})

        rows = sorted(rows, cmp=lambda x,y: cmp(x.lower(), y.lower()), key=itemgetter(sidx and sidx or 'BatchID'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[(int(page) - 1) * int(nr_rows): int(page) * int(nr_rows)]}

        return json.dumps(ret)
