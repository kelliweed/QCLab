from plone import api
from zope.component import getAdapters

from bika.lims.interfaces import IStorageTypeRegistration, \
    ISampleStorageLocation


def getStorageTypes(dotted_names=False):
    """Return interfaces and titles for all registered storage types.
    if dotted_names is True, then the interfaces returned will be converted to
    string identifiers.
    """
    types = []
    adapters = getAdapters((api.portal.get(),), IStorageTypeRegistration)
    for adaptername, storagetypes in adapters:
        if dotted_names:
            storagetypes = [
                {'interface': st['interface'].__identifier__,
                 'title': st['title']}
                for st in storagetypes]
        types.extend(storagetypes)
    return types


def defaultStorageTypes(context):
    """Return the storage types provided directly by bika.lims
    """
    return [{'interface': ISampleStorageLocation, 'title': 'Samples'}]
