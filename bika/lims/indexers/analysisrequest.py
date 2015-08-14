from plone.indexer import indexer

from bika.lims.interfaces import IAnalysisRequest


@indexer(IAnalysisRequest)
def RequestID(instance):
    return instance.getId()


@indexer(IAnalysisRequest)
def Retested(instance):
    for analysis in instance.getAnalyses(full_objects=True):
        if analysis.getRetested():
            return True
    return False


@indexer(IAnalysisRequest)
def Invoiced(instance):
    return instance.getInvoice() and True or False


@indexer(IAnalysisRequest)
def ProfileTitles(instance):
    return [profile.Title() for profile in instance.getProfiles()]


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
def ClientSampleID(instance):
    if hasattr(instance, 'getSample'):
        sample = instance.getSample()
        return sample.getClientSampleID()
