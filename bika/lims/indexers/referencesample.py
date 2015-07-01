from plone.indexer import indexer

from bika.lims.interfaces import IReferenceSample


@indexer(IReferenceSample)
def ReferenceDefinitionUID(instance):
    referencedefinition = instance.getReferenceDefintion()
    if referencedefinition:
        return referencedefinition.UID()
