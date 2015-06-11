from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from plone.app.layout.globals.interfaces import IViewView
from bika.lims.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from bika.lims.interfaces import IProducts

class ProductsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(ProductsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'Product',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=Product',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Products"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/product_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Title'),
                      'index': 'sortable_title'},
            'ProductCategory': {'title': _('Product Category'),
                           'index': 'getProductCategory',
                           'toggle': True},
            'Supplier': {'title': _('Supplier'),
                           'index': 'getSupplier',
                           'toggle': True},
            'Quantity': {'title': _('Quantity'),
                           'index': 'getQuantity',
                           'toggle': True},
            'Hazardous': {'title': _('Hazardous'),
                           'index': 'getHazardous',
                           'toggle': True},
            'Toxicity': {'title': _('Toxicity'),
                           'index': 'getToxicity',
                           'toggle': True},
        }
        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'ProductCategory',
                         'Supplier',
                         'Quantity',
                         'Hazardous',
                         'Toxicity']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'ProductCategory',
                         'Supplier',
                         'Quantity',
                         'Hazardous',
                         'Toxicity']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'ProductCategory',
                         'Supplier',
                         'Quantity',
                         'Hazardous',
                         'Toxicity']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['ProductCategory'] = obj.getProductCategory()
            items[x]['Supplier'] = obj.getSupplier()
            items[x]['Quantity'] = obj.getQuantity()
            items[x]['Hazardous'] = obj.getHazardous()
            items[x]['Toxicity'] = obj.getToxicity()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

        return items

schema = ATFolderSchema.copy()
class Products(ATFolder):
    implements(IProducts)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(Products, PROJECTNAME)