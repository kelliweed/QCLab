from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *
from plone.app.folder.folder import ATFolder
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IStorageLevel

Temperature = StringField(
    'Temperature',
    widget=StringWidget(
        label=_('Temperature'),
        description=_('If this level has a different temperature from '
                      'the parent object, it can be overridden here.'),
    ),
)

Containers = StringField(
    'Containers',
    widget=StringWidget(
        label=_('Containers'),
        description=_('If storage at this location is restricted to specific '
                      'containers, specify them here.'),
    ),
)

StorageTypes = LinesField(
    'StorageTypes',
    vocabulary="StorageTypesVocabulary",
    widget=MultiSelectionWidget(
        label=_("Storage Types"),
        format="checkbox",
    )
)

schema = BikaFolderSchema.copy() + Schema((
    Temperature,
    Containers,
    StorageTypes,
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

    def getHierarchy(self, structure=False, separator='.', fieldname='id'):
        ancestors = []
        ancestor = self
        while (1):
            accessor = getattr(ancestor, fieldname).getAccessor()
            val = accessor() if callable(accessor) else accessor
            if structure:
                ancestors.append(
                    "<a href='%s'>%s</a>" % (ancestor.absolute_url(), val))
            else:
                ancestors.append(val)
            if ancestor.portal_type == 'StorageUnit':
                break
            ancestor = ancestor.aq_parent
        return separator.join(reversed(ancestors))

    def StorageTypesVocabulary(self):
        items = [
            # ("bika.lims.interfaces.IItemStorageLocation",
            #  "Any type of item in the system"),
            # ("bika.lims.interfaces.ISampleItemStorageLocation",
            #  "Any type of Sample item"),
            ("bika.lims.interfaces.IBioSpecimenStorageLocation",
             "Bio Specimens"),
            ("bika.lims.interfaces.IAliquotStorageLocation",
             "Aliquots"),
            # ("bika.lims.interfaces.IInventoryStorageLocation",
            #  "Any type of Inventory item"),
            ("bika.lims.interfaces.IStockItemStorageLocation",
             "Stock Items (products)"),
            ("bika.lims.interfaces.IKitStorageLocation",
             "Kits")
        ]
        return DisplayList(zip(items[0], items[1]))


registerType(StorageLevel, PROJECTNAME)
