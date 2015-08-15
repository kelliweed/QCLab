"""Simple indexers for BikaSetup objects
"""

from plone.indexer import indexer
from zope.interface import Interface

@indexer(Interface)
def Accredited(instance):
    if hasattr(instance, 'getAccredited'):
        return instance.getAccredited()


@indexer(Interface)
def InstrumentType(instance):
    if hasattr(instance, 'getInstrumentType'):
        return instance.getInstrumentType()


@indexer(Interface)
def InstrumentTypeName(instance):
    if hasattr(instance, 'getInstrumentTypeName'):
        return instance.getInstrumentTypeName()


@indexer(Interface)
def Blank(instance):
    if hasattr(instance, 'getBlank'):
        return instance.getBlank()


@indexer(Interface)
def CalculationTitle(instance):
    if hasattr(instance, 'getCalculationTitle'):
        return instance.getCalculationTitle()


@indexer(Interface)
def CalculationUID(instance):
    if hasattr(instance, 'getCalculationUID'):
        return instance.getCalculationUID()


@indexer(Interface)
def CalibrationExpiryDate(instance):
    if hasattr(instance, 'getCalibrationExpiryDate'):
        return instance.getCalibrationExpiryDate()


@indexer(Interface)
def CategoryTitle(instance):
    if 'CategoryTitle' in instance.schema:
        return instance.schema['CategoryTitle'].get(instance)


@indexer(Interface)
def CategoryUID(instance):
    if 'CategoryUID' in instance.schema:
        return instance.schema['CategoryUID'].get(instance)


@indexer(Interface)
def ClientUID(instance):
    if hasattr(instance, 'getClientUID'):
        return instance.getClientUID()


@indexer(Interface)
def DepartmentTitle(instance):
    if hasattr(instance, 'getDepartmentTitle'):
        return instance.getDepartmentTitle()


@indexer(Interface)
def DuplicateVariation(instance):
    if hasattr(instance, 'getDuplicateVariation'):
        return instance.getDuplicateVariation()


@indexer(Interface)
def Formula(instance):
    if hasattr(instance, 'getFormula'):
        return instance.getFormula()


@indexer(Interface)
def Hazardous(instance):
    if hasattr(instance, 'getHazardous'):
        return instance.getHazardous()


@indexer(Interface)
def InstrumentTitle(instance):
    if hasattr(instance, 'getInstrumentTitle'):
        return instance.getInstrumentTitle()


@indexer(Interface)
def Keyword(instance):
    if hasattr(instance, 'getKeyword'):
        return instance.getKeyword()


@indexer(Interface)
def ManagerName(instance):
    if hasattr(instance, 'getManagerName'):
        return instance.getManagerName()


@indexer(Interface)
def ManagerPhone(instance):
    if hasattr(instance, 'getManagerPhone'):
        return instance.getManagerPhone()


@indexer(Interface)
def ManagerEmail(instance):
    if hasattr(instance, 'getManagerEmail'):
        return instance.getManagerEmail()


@indexer(Interface)
def MaxTimeAllowed(instance):
    if hasattr(instance, 'getMaxTimeAllowed'):
        return instance.getMaxTimeAllowed()


@indexer(Interface)
def Model(instance):
    if hasattr(instance, 'getModel'):
        return instance.getModel()


@indexer(Interface)
def Name(instance):
    if hasattr(instance, 'getName'):
        return instance.getName()


@indexer(Interface)
def PointOfCapture(instance):
    if hasattr(instance, 'getPointOfCapture'):
        return instance.getPointOfCapture()


@indexer(Interface)
def Price(instance):
    if hasattr(instance, 'getPrice'):
        return instance.getPrice()


@indexer(Interface)
def SamplePointTitle(instance):
    if hasattr(instance, 'getSamplePointTitle'):
        return instance.getSamplePointTitle()


@indexer(Interface)
def SamplePointUID(instance):
    if hasattr(instance, 'getSamplePointUID'):
        return instance.getSamplePointUID()


@indexer(Interface)
def SampleTypeTitle(instance):
    if hasattr(instance, 'getSampleTypeTitle'):
        return instance.getSampleTypeTitle()


@indexer(Interface)
def SampleTypeUID(instance):
    if hasattr(instance, 'getSampleTypeUID'):
        return instance.getSampleTypeUID()


@indexer(Interface)
def ServiceTitle(instance):
    if hasattr(instance, 'getServiceTitle'):
        return instance.getServiceTitle()


@indexer(Interface)
def ServiceUID(instance):
    if hasattr(instance, 'getServiceUID'):
        return instance.getServiceUID()


@indexer(Interface)
def TotalPrice(instance):
    if hasattr(instance, 'getTotalPrice'):
        return instance.getTotalPrice()


@indexer(Interface)
def Unit(instance):
    if hasattr(instance, 'getUnit'):
        return instance.getUnit()


@indexer(Interface)
def VATAmount(instance):
    if hasattr(instance, 'getVATAmount'):
        return instance.getVATAmount()


@indexer(Interface)
def Volume(instance):
    if hasattr(instance, 'getVolume'):
        return instance.getVolume()


@indexer(Interface)
def sortKey(instance):
    if hasattr(instance, 'getsortKey'):
        return instance.getsortKey()


@indexer(Interface)
def MethodID(instance):
    if hasattr(instance, 'getMethodID'):
        return instance.getMethodID()


@indexer(Interface)
def DocumentID(instance):
    if hasattr(instance, 'getDocumentID'):
        return instance.getDocumentID()
