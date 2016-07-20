from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *
from Products.CMFPlone.utils import safe_unicode

from bika.lims import bikaMessageFactory as _, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema

StorageTypes = LinesField(
    'StorageTypes',
    vocabulary="StorageTypesVocabulary",
    accessor="getLabelNames",
    widget=MultiSelectionWidget(
        label=_("Storage Types"),
        format="checkbox",
    )
)

schema = BikaSchema.copy() + Schema((
    StorageTypes,
))
schema['title'].widget.label = _('Address')
schema['description'].widget.visible = True


class StorageLocation(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        return safe_unicode(self.getField('title').get(self)).encode('utf-8')

    def StorageTypesVocabulary(self):
        items = [
            ("bika.lims.interfaces.IItemStorageLocation",
             "Any type of item in the system"),
            ("bika.lims.interfaces.ISampleItemStorageLocation",
             "Any type of Sample item"),
            ("bika.lims.interfaces.IBioSpecimenStorageLocation",
             "Bio Specimens"),
            ("bika.lims.interfaces.IAliquotStorageLocation",
             "Aliquots"),
            ("bika.lims.interfaces.IInventoryStorageLocation",
             "Any type of Inventory item"),
            ("bika.lims.interfaces.IStockItemStorageLocation",
             "Stock Items (products"),
            ("bika.lims.interfaces.IKitStorageLocation",
             "Kits")
        ]
        return DisplayList(zip(items[0], items[1]))

    def getStoredItem(self):
        items = self.getBackReferences('StoredItemStorageLocation')
        if items:
            return items[0]

    def guard_occupy_transition(self):
        """Occupy transition cannot proceed until StoredItem is set.

        If this position is free, but also has a StoredItem set,
        then we will prevent the occupy transition from becoming available.
        """
        wftool = self.portal_workflow
        review_state = wftool.getInfoFor(self, 'review_state')
        if (review_state == 'free' or review_state == 'reserved') \
                and self.getStoredItem():
            return True
        return False

    def guard_free_transition(self):
        """Free transition cannot proceed unless StoredItem is cleared.

        If this position is occupied and StoredItem still has a value,
        then we will prevent the free transition from becoming available.
        """
        wftool = self.portal_workflow
        review_state = wftool.getInfoFor(self, 'review_state')
        if review_state in ('occupied', 'reserved') \
                and not self.getStoredItem():
            return True
        return False

    def at_post_create_script(self):
        """Execute once the object is created
        """
        wftool = self.portal_workflow
        if self.guard_occupy_transition():
            wftool.doActionFor(self, action='occupy',
                               wf_id='bika_storageposition_workflow')

    def at_post_edit_script(self):
        """Execute once the object is edited
        """
        wftool = self.portal_workflow
        if self.guard_free_transition():
            wftool.doActionFor(self, action='free',
                               wf_id='bika_storageposition_workflow')
        if self.guard_occupy_transition():
            wftool.doActionFor(self, action='occupy',
                               wf_id='bika_storageposition_workflow')


registerType(StorageLocation, PROJECTNAME)
