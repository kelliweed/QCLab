from bika.lims.interfaces import ISample
from plone.indexer import indexer

@indexer(ISample)
def DateReceived(instance):
    return instance.getDateReceived()