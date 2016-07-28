from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from bika.lims import bikaMessageFactory as _, PROJECTNAME
from bika.lims.browser.storage import getStorageTypes
from bika.lims.content.bikaschema import BikaSchema

schema = BikaSchema.copy() + Schema((
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

    def getHierarchy(self, structure=False, separator='.', fieldname='id'):
        ancestors = []
        ancestor = self
        while (1):
            try:
                accessor = getattr(ancestor, fieldname).getAccessor()
                val = accessor() if callable(accessor) else accessor
            except AttributeError:
                val = getattr(ancestor, fieldname)
            if structure:
                ancestors.append(
                    "<a href='%s'>%s</a>" % (ancestor.absolute_url(), val))
            else:
                ancestors.append(val)
            if ancestor.portal_type == 'StorageUnit':
                break
            ancestor = ancestor.aq_parent
        return separator.join(reversed(ancestors))

    def getStorageTypes(self):
        """Return a list of the storage type interfaces which are provided here.
        """
        return [x for x in getStorageTypes() if x['interface'].providedBy(self)]

    def getStoredItem(self):
        items = self.getBackReferences('StoredItemStorageLocation')
        if items:
            return items[0]

    def guard_occupy_transition(self):
        """Occupy transition cannot proceed until StoredItem is set.

        If this position is available, but also has a StoredItem set,
        then we will prevent the occupy transition from becoming available.
        """
        wftool = self.portal_workflow
        review_state = wftool.getInfoFor(self, 'review_state')
        if (review_state == 'available' or review_state == 'reserved') \
                and self.getStoredItem():
            return True
        return False

    def workflow_script_occupy(self):
        """If possible, occupy the parent storage level.
        """
        wf = getToolByName(self, 'portal_workflow')
        tids = [t['id'] for t in wf.getTransitionsFor(self.aq_parent)]
        if 'occupy' in tids:
            wf.doActionFor(self.aq_parent, 'occupy')

    def guard_liberate_transition(self):
        """Liberate transition cannot proceed unless StoredItem is cleared.

        If this position is occupied and StoredItem still has a value,
        then we will prevent the liberate transition from becoming available.
        """
        wftool = self.portal_workflow
        review_state = wftool.getInfoFor(self, 'review_state')
        if review_state in ('occupied', 'reserved') \
                and not self.getStoredItem():
            return True
        return False

    def workflow_script_liberate(self):
        """If possible, liberate the parent storage level.
        """
        wf = getToolByName(self, 'portal_workflow')
        tids = [t['id'] for t in wf.getTransitionsFor(self.aq_parent)]
        if 'liberate' in tids:
            wf.doActionFor(self.aq_parent, 'liberate')

    def available(self):
        wf = getToolByName(self, 'portal_workflow')
        return wf.getInfoFor(self, 'review_state') == 'available'

    def at_post_create_script(self):
        """Execute once the object is created
        """
        wftool = self.portal_workflow
        if self.guard_occupy_transition():
            wftool.doActionFor(
                self, action='occupy', wf_id='bika_storagelocation_workflow')

    def at_post_edit_script(self):
        """Execute once the object is edited
        """
        wftool = self.portal_workflow
        if self.guard_liberate_transition():
            wftool.doActionFor(
                self, action='liberate', wf_id='bika_storagelocation_workflow')
        if self.guard_occupy_transition():
            wftool.doActionFor(
                self, action='occupy', wf_id='bika_storagelocation_workflow')


registerType(StorageLocation, PROJECTNAME)
