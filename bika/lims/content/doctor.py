"""
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_users
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.config import *
from bika.lims.interfaces import IDoctor
from bika.lims.permissions import *
from bika.lims.content.contact import Contact
from bika.lims import PMF, bikaMessageFactory as _
from zope.interface import implements

schema = Schema((
   StringField('DoctorID',
        searchable=True,
        write_permission=ManageBika,
        widget=StringWidget(
            label=_('Doctor ID'),
        ),
    ),
)) + Contact.schema.copy() + Schema((
    StringField('DoctorRole',
        required=1,
        default='Doctor',
        vocabulary=PROVIDER_ROLES,
        write_permission=ManageDoctors,
        widget=SelectionWidget(
            label=_('Doctor Role'),
        ),
    ),
))

schema['DoctorID'].validators = ('uniquefieldvalidator',)
# Update the validation layer after change the validator in runtime
schema['DoctorID']._validationLayer()

class Doctor(Contact):
    implements(IDoctor)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    # This is copied from Client (Contact acquires it, but we cannot)
    security.declarePublic('getContactsDisplayList')
    def getContactsDisplayList(self):
        pc = getToolByName(self, 'portal_catalog')
        pairs = []
        for contact in pc(portal_type = 'Contact',
                          inactive_state = 'active'):
            pairs.append((contact.UID, contact.title))
        # sort the list by the second item
        pairs.sort(lambda x, y:cmp(x[1], y[1]))
        return DisplayList(pairs)

    # This is copied from Contact (In contact, it refers to the parent's
    # getContactsDisplayList, while we define our own
    security.declarePublic('getCCContactsDisplayList')
    def getCCContactsDisplayList(self):
        pairs = []
        all_contacts = self.getContactsDisplayList().items()
        # remove myself
        for item in all_contacts:
            if item[0] != self.UID():
                pairs.append((item[0], item[1]))
        return DisplayList(pairs)

atapi.registerType(Doctor, PROJECTNAME)
