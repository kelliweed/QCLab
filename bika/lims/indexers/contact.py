from Acquisition._Acquisition import aq_base

from plone.indexer import indexer

from bika.lims import logger

from bika.lims.interfaces import IContact


@indexer(IContact)
def ParentUID(instance):
    logger.info("IContact ParentUID is called on %s"%instance)
    if hasattr(instance, 'aq_parent'):
        return getattr(aq_base(instance.aq_parent), 'UID', None)


@indexer(IContact)
def Fullname(instance):
    return instance.getFullname()


@indexer(IContact)
def Username(instance):
    return instance.getUsername()
