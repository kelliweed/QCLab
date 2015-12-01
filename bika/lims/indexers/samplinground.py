from bika.lims.interfaces import ISamplePartition
from plone.indexer import indexer

@indexer(ISamplePartition)
def Preserver(instance):
    return instance.getPreserver()
