from bika.lims.interfaces import IAnalysisRequest
from plone.indexer import indexer

@indexer(IAnalysisRequest)
def DateReceived(instance):
    return instance.getDateReceived()