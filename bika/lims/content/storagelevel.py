from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *
from plone.app.folder.folder import ATFolder
from zope.interface import implements

from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IStorageLevel

schema = BikaFolderSchema.copy() + Schema((

))


class StorageLevel(ATFolder):
    implements(IStorageLevel)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation

        renameAfterCreation(self)

    def getHierarchy(self):
        # use aq_chain here
        ancestors = []
        ancestor = self
        while (1):
            ancestors.append(ancestor.Title())
            if ancestor.portal_type == 'StorageUnit':
                break
            ancestor = ancestor.aq_parent
        return ' > '.join(reversed(ancestors))


registerType(StorageLevel, PROJECTNAME)
