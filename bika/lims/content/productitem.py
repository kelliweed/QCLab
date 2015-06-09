from zope.interface import implements
from Products.Archetypes import atapi
from bika.lims import bikaMessageFactory as _
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from bika.lims.interfaces import IProductItem
from bika.lims import config
from bika.lims.content.bikaschema import BikaSchema
from DateTime.DateTime import DateTime
from Products.Archetypes.public import *

schema = BikaSchema.copy() + Schema((
    StringField('orderId',
        widget = StringWidget(
            label=_("Order Id"),
        )
    ),
    StringField('labId',
        widget = StringWidget(
            label=_("Lab Id"),
        )
    ),
    StringField('batchId',
        widget = StringWidget(
            label=_("Batch Id"),
        )
    ),
    StringField('location',
        widget = StringWidget(
            label=_("Location"),
        )
    ),
    DateTimeField('dateReceived',
        searchable = 1,
        required = 0,
        widget = CalendarWidget(
            label = 'Date Received'
        ),
    ),
    DateTimeField('dateOpened',
        searchable = 1,
        required = 0,
        widget = CalendarWidget(
            label = 'Date Opened'
        ),
    ),
    DateTimeField('expiryDate',
        searchable = 1,
        required = 0,
        widget = CalendarWidget(
            label = 'Expiry Date'
        ),
    ),
    DateTimeField('disposalDate',
        searchable = 1,
        required = 0,
        widget = CalendarWidget(
            label = 'Disposal Date'
        ),
    ),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True

class ProductItem(BaseContent):
	implements(IProductItem)
	schema = schema
	
	_at_rename_after_creation = True

	def _renameAfterCreation(self, check_auto_id=False):
		from bika.lims.idserver import renameAfterCreation
		renameAfterCreation(self)

registerType(ProductItem, config.PROJECTNAME)