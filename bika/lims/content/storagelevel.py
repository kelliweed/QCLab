from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from plone.app.folder.folder import ATFolder
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.storage import getStorageTypes
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

schema = BikaFolderSchema.copy() + Schema((
    Temperature,
    Containers
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

    def guard_occupy_transition(self):
        """Occupy transition signifies that this storage level cannot accept
        further items for storage.

        For managed storage levels, this transition is allowed when all
        available storage locations are occupied.

        For un-managed storage levels this transition is always available
        to be triggered manually.
        """
        locs = self.objectValues('StorageLocation')
        if locs:
            # managed storage level: allow if no child locations are available.
            availables = [loc for loc in locs if loc.available()]
            if not availables:
                return True
        else:
            # unmanaged storage level: always permit transition.
            return True

    def guard_liberate_transition(self):
        """Liberate transition means this level can now be selected as
        an item's storage location.

        For managed storage levels, this transition is allowed when some
        available storage locations are available.

        For un-managed storage levels this transition is always available.
        """
        locs = self.objectValues('StorageLocation')
        if locs:
            # managed storage level: allow if no child locations are available.
            availables = [loc for loc in locs if loc.available()]
            if availables:
                return True
        else:
            # unmanaged storage level: always permit transition.
            return True

    def available(self):
        wf = getToolByName(self, 'portal_workflow')
        return wf.getInfoFor(self, 'review_state') == 'available'


registerType(StorageLevel, PROJECTNAME)
