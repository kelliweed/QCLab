from bika.lims.interfaces import IAnalysisRequest
from bika.lims.utils import get_transition_info
from plone.indexer import indexer


@indexer(IAnalysisRequest)
def SamplingDate(instance):
    return instance.getSamplingDate()


@indexer(IAnalysisRequest)
def DateSampled(instance):
    sample = instance.getSample()
    if sample:
        return sample.getDateSampled()


@indexer(IAnalysisRequest)
def DateReceived(instance):
    return get_transition_info(instance, 'recieve', 'time')


@indexer(IAnalysisRequest)
def DatePublished(instance):
    return get_transition_info(instance, 'publish', 'time')


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
def Priority(instance):
    priority = instance.getPriority()
    if priority:
        return priority.getSortKey()


@indexer(IAnalysisRequest)
def Analysts(instance):
    analysts = []
    for analysis in instance.objectValues("Analysis"):
        analyst = analysis.getAnalyst()
        if analyst not in analysts:
            analysts.append(analyst)
    return analysts


@indexer(IAnalysisRequest)
def ContactTitle(instance):
    contact = instance.getContact()
    if contact:
        return contact.Title()


@indexer(IAnalysisRequest)
def BatchUID(instance):
    batch = instance.getBatch()
    if batch:
        return batch.UID()


@indexer(IAnalysisRequest)
def ParentUID(instance):
    return instance.aq_parent.UID()


@indexer(IAnalysisRequest)
def ClientTitle(instance):
    client = instance.getClient()
    if client:
        return client.Title()


@indexer(IAnalysisRequest)
def ClientUID(instance):
    client = instance.getClient()
    if client:
        return client.UID()


@indexer(IAnalysisRequest)
def ClientOrderNumber(instance):
    return instance.getClientOrderNumber()


@indexer(IAnalysisRequest)
def ClientReference(instance):
    return instance.getClientReference()


@indexer(IAnalysisRequest)
def ClientSampleID(instance):
    return instance.getClientSampleID()


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
