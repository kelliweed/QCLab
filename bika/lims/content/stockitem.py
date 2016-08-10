from zope.interface import implements
from Products.Archetypes import atapi
from bika.lims import bikaMessageFactory as _
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from bika.lims.browser.widgets import DateTimeWidget as bika_DateTimeWidget
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.interfaces import IStockItem
from bika.lims import config
from bika.lims.content.bikaschema import BikaSchema
from DateTime.DateTime import DateTime
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
import sys

schema = BikaSchema.copy() + Schema((
    ReferenceField('Product',
        required=1,
        vocabulary_display_path_bound=sys.maxint,
        allowed_types=('Product', 'Kit'),
        relationship='StockItemProduct',
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
            label=_("Product"),
            catalog_name='bika_setup_catalog',
            showOn=False,
            description=_("Start typing to filter the list of available products."),
        ),
    ),

    # ComputedField('SupplierTitle',
    #     expression='context.getProduct().getSupplierTitle()',
    #     widget=ComputedWidget(
    #         label=_("Supplier"),
    #         visible={'edit':'hidden', }
    #     ),
    # ),

    ComputedField('ProductTitle',
        expression='context.getProduct().Title()',
        widget=ComputedWidget(
          label=_("Product Title"),
          visible={'edit':'hidden'}
        ),
    ),

    ComputedField('ProductID',
        expression="context.getProduct() and context.getProduct().getId() or ''",
        widget=ComputedWidget(
            label=_("Product Title"),
            visible={'edit': 'hidden'}
        ),
    ),

    ComputedField('ProductCategoryTitle',
        expression='context.getProduct().getCategoryTitle()',
        widget=ComputedWidget(
            label=_("Product Category"),
            visible={'edit':'hidden', }
        ),
    ),

    IntegerField('Quantity',
        required=1,
        widget=IntegerWidget(
            label=_("Quantity"),
            description=_("The number of product items that this stock item represents."),
        ),
    ),

    StringField('orderId',
        widget = StringWidget(
            label=_("Invoice Number"),
        )
    ),

    StringField('batchId',
        widget=StringWidget(
            label=_("Batch Id"),
        )
    ),

    StringField('location',
        widget=StringWidget(
            label=_("Location"),
        )
    ),

    StringField('receivedBy',
        widget=StringWidget(
            label=_("Received By"),
            description="Provide full-name of the person receiving the current product in stock."
        )
    ),

    DateTimeField('dateReceived',
        searchable=1,
        widget=bika_DateTimeWidget(
            label='Date Received'
        ),
    ),

    DateTimeField('dateOpened',
        searchable=1,
        widget=bika_DateTimeWidget(
            label='Date Opened'
        ),
    ),

    DateTimeField('expiryDate',
        searchable=1,
        widget=bika_DateTimeWidget(
            label='Expiry Date'
        ),
    ),

    DateTimeField('disposalDate',
        searchable=1,
        widget=bika_DateTimeWidget(
            label='Disposal Date'
        ),
    ),

    BooleanField(
        'IsStored',
        default=False,
        widget=BooleanWidget(visible=False),
    ),

    StringField('StorageLevelID',
        widget=StringWidget(
            label=_("Location"),
        )
    ),
))

schema['title'].required = False
schema['title'].widget.visible = False
schema['description'].schemata = 'default'
schema['description'].widget.visible = True
schema.moveField('Product', before='description')

class StockItem(BaseContent):
    implements(IStockItem)
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)
        #self.at_post_create_script()

    def getProductTitle(self):
        return self.getProduct() and self.getProduct().Title() or ''

    def getStockItemId(self):
        return self.getId()

    #______HOCINE ADDED IT_________#
    def at_post_create_script(self):
        title = self.getProductTitle()
        self.setTitle(title)

registerType(StockItem, config.PROJECTNAME)
