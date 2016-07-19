from Products.Archetypes import atapi
from plone.app.folder.folder import ATFolder
from zope.interface.declarations import implements

from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IStorageUnits

schema = BikaSchema.copy()


class StorageUnits(ATFolder):
    implements(IStorageUnits)
    displayContentsTab = False
    schema = schema


atapi.registerType(StorageUnits, PROJECTNAME)
