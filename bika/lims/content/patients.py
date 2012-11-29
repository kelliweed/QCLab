from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IPatients
from bika.lims.permissions import *
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements
import json

class PatientsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(PatientsView, self).__init__(context, request)

        self.catalog = 'bika_patient_catalog'

        self.contentFilter = {'portal_type': 'Patient',
                              'sort_on': 'sortable_title'}
        self.context_actions = {}
        self.title = _("Patients")
        self.icon = "++resource++bika.lims.images/patient_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25

        self.columns = {

            'Title': {'title': _('Patient'),
                      'index': 'sortable_title'},

            'getPatientID': {'title': _('Patient ID'),
                             'index': 'getPatientID'},

            'getGender': {'title': _('Gender'),
                       'index': 'getGender',
                       'toggle': True},

            'getAge': {'title': _('Age'),
                   'index': 'getAge',
                   'toggle': True},

            'getBirthDate': {'title': _('BirthDate'),
                            'index':'getBirthDate',
                            'toggle': True},

            'getCitizenship': {'title': _('Citizenship'),
                          'index':'getCitizenship',
                          'toggle': True},

            'getPrimaryReferrer' : {'title': _('Primary Referrer'),
                                    'index': 'getPrimaryReferrer',
                                    'toggle': True},

  #          'Description': {'title': _('Description'),
  #                          'index': 'Description',
  #                          'toggle': True},
        }

        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions':[{'id':'empty'},],
             'columns': ['Title', 'getPatientID', 'getGender', 'getAge',
                         'getBirthDate', 'getCitizenship', 'getPrimaryReferrer']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        addPortalMessage = self.context.plone_utils.addPortalMessage
        if mtool.checkPermission(AddPatient, self.context):
            clients = self.context.clients.objectIds()
            if clients:
                self.context_actions[_('Add')] = {
                    'url': 'createObject?type_name=Patient',
                    'icon': '++resource++bika.lims.images/add.png'
                }
            else:
                msg = _("Cannot create patients without any system clients configured.")
                addPortalMessage(self.context.translate(msg))
        return super(PatientsView, self).__call__()

    def folderitems(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(ManagePatients, self.context):
            del self.review_states[0]['transitions']
            self.show_select_column = True
            self.review_states.append(
                {'id':'active',
                 'title': _('Active'),
                 'contentFilter': {'inactive_state': 'active'},
                 'transitions': [{'id':'deactivate'}, ],
                 'columns': ['getPatientID', 'Title', 'getGender', 'getAge',
                             'getBirthDate', 'getCitizenship', 'getPrimaryReferrer']})
            self.review_states.append(
                {'id':'inactive',
                 'title': _('Dormant'),
                 'contentFilter': {'inactive_state': 'inactive'},
                 'transitions': [{'id':'activate'}, ],
                 'columns': ['getPatientID', 'Title', 'getGender', 'getAge',
                             'getBirthDate', 'getCitizenship', 'getPrimaryReferrer']})

        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['getPatientID'] = obj.getPatientID()
            items[x]['getBirthDate'] = self.ulocalized_time(obj.getBirthDate())
            items[x]['replace']['getPatientID'] = "<a href='%s/analysisrequests'>%s</a>" % \
                 (items[x]['url'], items[x]['getPatientID'])
            items[x]['replace']['Title'] = "<a href='%s/analysisrequests'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

            pr = obj.getPrimaryReferrer()
            if pr:
                items[x]['getPrimaryReferrer'] = pr.Title()
                items[x]['replace']['getPrimaryReferrer'] = "<a href='%s/analysisrequests'>%s</a>" % \
                     (pr.absolute_url(), pr.Title())
            else:
                items[x]['getPrimaryReferrer'] = ''

        return items

schema = ATFolderSchema.copy()
class Patients(ATFolder):
    implements(IPatients)
    displayContentsTab = False
    schema = schema

    def getContacts(self, dl=True):
        pc = getToolByName(self, 'portal_catalog')
        bc = getToolByName(self, 'bika_catalog')
        bsc = getToolByName(self, 'bika_setup_catalog')
        pairs = []
        objects = []
        client = None
        client = self.getPrimaryReferrer()
        if client:
            for contact in client.objectValues('Contact'):
                if isActive(contact):
                    pairs.append((contact.UID(), contact.Title()))
                    if not dl:
                        objects.append(contact)
            pairs.sort(lambda x, y:cmp(x[1].lower(), y[1].lower()))
            return dl and DisplayList(pairs) or objects
        # fallback - all Lab Contacts
        for contact in bsc(portal_type = 'LabContact',
                           inactive_state = 'active',
                           sort_on = 'sortable_title'):
            pairs.append((contact.UID, contact.Title))
            if not dl:
                objects.append(contact.getObject())
        return dl and DisplayList(pairs) or objects

    def getCCs(self):
        """Return a JSON value, containing all Contacts and their default CCs.
           This function is used to set form values for javascript.
        """
        items = []
        for contact in self.getContacts(dl=False):
            item = {'uid': contact.UID(), 'title': contact.Title()}
            ccs = []
            if hasattr(contact, 'getCCContact'):
                for cc in contact.getCCContact():
                    if isActive(cc):
                        ccs.append({'title': cc.Title(),
                                    'uid': cc.UID(),})
            item['ccs_json'] = json.dumps(ccs)
            item['ccs'] = ccs
            items.append(item)
        items.sort(lambda x, y:cmp(x['title'].lower(), y['title'].lower()))
        return items

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(Patients, PROJECTNAME)
