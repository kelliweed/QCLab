from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *
from Products.CMFPlone.utils import safe_unicode

from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema

schema = BikaSchema.copy() + Schema((
    StringField('LocationCode',
                widget=StringWidget(
                    label=_("Location Code"),
                    description=_("Code for the location"),
                ),
                ),
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


registerType(StorageLocation, PROJECTNAME)
