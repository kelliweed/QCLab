from zope.interface import implements
from Products.Archetypes import atapi
from bika.lims import bikaMessageFactory as _
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.CMFCore.utils import getToolByName
from bika.lims.interfaces import IProduct
from bika.lims import config
from bika.lims.content.bikaschema import BikaSchema
from DateTime.DateTime import DateTime
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
import sys

schema = BikaSchema.copy() + Schema((
    ReferenceField('ProductCategory',
        required=1,
        vocabulary='getProductCategories',
        allowed_types=('ProductCateogory',),
        relationship='ProductProductCategory',
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
            checkbox_bound=0,
            label = _("Product Category"),
            description = _(""),
        ),
    ),
    ReferenceField('Supplier',
        required=1,
        vocabulary='getSuppliers',
        allowed_types=('Supplier',),
        relationship='ProductSupplier',
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
            checkbox_bound=0,
            label = _("Supplier"),
        ),
    ),
    StringField('CAS',
        searchable = True,
        widget = StringWidget(
            label=_("CAS Registry Number"),
        ),
    ),
    StringField('SupplierCatalogueID',
        searchable = True,
        widget = StringWidget(
            label=_("Supplier Catalogue ID"),
        ),
    ),
    BooleanField('Hazardous',
        default = False,
        widget = BooleanWidget(
            label=_("Hazardous"),
            description=_("Samples of this type should be treated as hazardous"),
        ),
    ),
    StringField('Quantity',
        widget = StringWidget(
            label=_("Quantity"),
            description=_("The quantity of the product already in storage eg. '10 ml' or '1 kg'."),
        ),
    ),
    StringField('Toxicity',
        widget = StringWidget(
            label=_("Toxicity"),
            description=_("Toxic exposure limit eg. 25 ppm (8hr TWA)"),
        ),
    ),
    TextField('HealthEffects',
        default_output_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget=TextAreaWidget (
            label = _("Health Effects")),
    ),
    TextField('FirstAidSOP',
        default_output_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget=TextAreaWidget (
            label = _("First Aid SOP")),
            description=_("Standard operating procedures for first aid."),
    ),
    TextField('StorageConditions',
        default_output_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget=TextAreaWidget (
            label = _("Storage Conditions")),
            description=_("Requirements for storing the product."),
    ),
    TextField('DisposalSOP',
        default_output_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget=TextAreaWidget (
            label = _("Disposal SOP")),
            description=_("Standard operating procedures for disposal of the product."),
    ),
    TextField('SpillHandlingSOP',
        default_output_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget=TextAreaWidget (
            label = _("Spill-handling SOP")),
            description=_("Standard operating procedures for handling spillage of the product."),
    ),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True

class Product(BaseContent):
    implements(IProduct)
    schema = schema
    
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getSuppliers(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(c.UID, c.getName) \
                for c in bsc(portal_type='Supplier',
                             inactive_state = 'active')]
        items.sort(lambda x,y:cmp(x[1], y[1]))
        return DisplayList(items)

    def getProductCategories(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        deps = []
        for d in bsc(portal_type='ProductCategory',
                     inactive_state='active'):
            deps.append((d.UID, d.Title))
        return DisplayList(deps)

registerType(Product, config.PROJECTNAME)