from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims.browser import BrowserView
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
from plone.app.collection.collection import Collection
from bika.lims.browser.fields import CoordinateField
from bika.lims.browser.widgets import CoordinateWidget
from bika.lims.browser.fields import DurationField
from bika.lims.browser.widgets import DurationWidget
from bika.lims import PMF, bikaMessageFactory as _
from zope.interface import implements
import json
import plone
import sys


class ReportCollection(Collection):
    security = ClassSecurityInfo()
    displayContentsTab = False

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        return safe_unicode(self.getField('title').get(self)).encode('utf-8')


registerType(ReportCollection, PROJECTNAME)