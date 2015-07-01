from plone.indexer import indexer

from bika.lims.interfaces import IAnalysis, IAnalysisRequest


@indexer(IAnalysis)
def RequestID(instance):
    if IAnalysisRequest.providedBy(instance.aq_parent):
        return instance.aq_parent.getRequestID()


@indexer(IAnalysis)
def Retested(instance):
    return instance.getRetested()


@indexer(IAnalysis)
def ReferenceAnalysesGroupID(instance):
    # reference analyses are also IAnalysis
    if hasattr(instance, 'getReferenceAnalysesGroupID'):
        return instance.getReferenceAnalysesGroupID()


@indexer(IAnalysis)
def PointOfCapture(instance):
    service = instance.getService()
    if service:
        return service.getPointOfCapture()
