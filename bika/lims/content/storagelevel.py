from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IStorageLevel
from plone.app.folder.folder import ATFolder
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from zope.interface import implements

schema = BikaFolderSchema.copy() + BikaSchema.copy() + Schema((
    ComputedField('ParentUID',
        expression = 'context.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True

class StorageLevel(ATFolder):
    implements(IStorageLevel)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(StorageLevel, PROJECTNAME)
