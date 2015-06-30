from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFPlone.utils import safe_unicode
from bika.lims.config import PROJECTNAME
from plone.app.collection.collection import Collection
from bika.lims import PMF, bikaMessageFactory as _
from zope.interface import implements

schema = Collection.schema
schema['limit'].widget.visible = False
schema['text'].widget.visible = False
schema['customViewFields'].widget.visible = False
schema['b_size'].widget.visible = False


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