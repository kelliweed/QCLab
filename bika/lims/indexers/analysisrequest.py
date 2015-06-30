from bika.lims.interfaces import IAnalysisRequest
from plone.indexer import indexer


@indexer(IAnalysisRequest)
def RequestID(instance):
    return instance.id


@indexer(IAnalysisRequest)
def Invoiced(instance):
    return instance.getInvoice() and True or False


@indexer(IAnalysisRequest)
def ProfileTitle(instance):
    profile = instance.getProfile()
    if profile:
        return profile.Title()


@indexer(IAnalysisRequest)
def Analysts(instance):
    analysts = []
    for analysis in instance.objectValues("Analysis"):
        analyst = analysis.getAnalyst()
        if analyst not in analysts:
            analysts.append(analyst)
    return analysts


@indexer(IAnalysisRequest)
def BatchUID(instance):
    batch = instance.getBatch()
    if batch:
        return batch.UID()


@indexer(IAnalysisRequest)
def SampleID(instance):
    sample = instance.getSample()
    if sample:
        return sample.id


@indexer(IAnalysisRequest)
def SampleUID(instance):
    sample = instance.getSample()
    if sample:
        return sample.UID()


@indexer(IAnalysisRequest)
def Sampler(instance):
    sample = instance.getSample()
    if sample:
        return sample.getSampler()


@indexer(IAnalysisRequest)
def SamplePointTitle(instance):
    sample = instance.getSample()
    if sample:
        return sample.getSamplePoint().Title()


@indexer(IAnalysisRequest)
def SamplePointUID(instance):
    sample = instance.getSample()
    if sample:
        return sample.getSamplePoint().UID()


@indexer(IAnalysisRequest)
def SampleTypeTitle(instance):
    sample = instance.getSample()
    if sample:
        return sample.getSampleType().Title()


@indexer(IAnalysisRequest)
def SampleTypeUID(instance):
    sample = instance.getSample()
    if sample:
        return sample.getSampleType().UID()
