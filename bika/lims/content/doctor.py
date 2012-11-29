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

schema = Contact.schema.copy() + Schema((
    StringField('DoctorID',
        required=1,
        widget=StringWidget(
            label=_('Doctor ID'),
        ),
    ),
))

class Doctor(Contact):
    implements(IDoctor)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    security.declarePublic('getSamples')
    def getSamples(self):
        """ get all samples taken from this Patient """
        bc = getToolByName(self, 'bika_catalog')
        return [p.getObject() for p in bc(portal_type='Sample', getDoctorUID=self.UID())]

    security.declarePublic('getARs')
    def getARs(self, analysis_state):
        bc = getToolByName(self, 'bika_catalog')
        return [p.getObject() for p in bc(portal_type='AnalysisRequest', getDoctorUID=self.UID())]

atapi.registerType(Doctor, PROJECTNAME)
