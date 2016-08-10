from plone import api
from zope.component import getAdapters

from bika.lims.interfaces import IStorageTypeRegistration
from bika.lims.interfaces import ISampleStorageLocation

def getStorageTypes():
    """Return interfaces and titles for all registered storage types.
    """

    output_types = []
    adapters = getAdapters((api.portal.get(),), IStorageTypeRegistration)
    for name, storagetypes in adapters:
        output_types.extend(storagetypes)
    return output_types


def defaultStorageTypes(context):
    """Return the storage types provided directly by bika.lims
    """
    return [{'interface': ISampleStorageLocation,
             'identifier': ISampleStorageLocation.__identifier__,
             'title': 'Samples'}]
