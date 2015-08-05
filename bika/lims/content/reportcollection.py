# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from OFS.ObjectManager import ObjectManager
from archetypes.querywidget.field import QueryField
from archetypes.querywidget.widget import QueryWidget
from bika.lims import to_utf8
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IReportCollection
from plone.app.collection.interfaces import ICollection
from plone.app.contentlisting.interfaces import IContentListing
from Products.ATContentTypes.content import document, schemata
from Products.Archetypes import atapi
from Products.Archetypes.atapi import (BooleanField,
                                       BooleanWidget,
                                       IntegerField,
                                       LinesField,
                                       IntegerWidget,
                                       InAndOutWidget,
                                       StringField,
                                       StringWidget)
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

from plone.app.collection import PloneMessageFactory as _
from plone.app.collection.config import ATCT_TOOLNAME
from plone.app.collection.marshaller import CollectionRFC822Marshaller
from plone.app.folder.folder import ATFolder
from bika.lims import PROJECTNAME

ReportCollectionSchema = BikaFolderSchema.copy() + atapi.Schema((

    QueryField(
        name='query',
        widget=QueryWidget(
            label=_(u"Search terms"),
            description=_(u"Define the search terms for the items you want to "
                          u"list by choosing what to match on. "
                          u"The list of results will be dynamically updated."),
        ),
        validators=('javascriptDisabled',)
    ),

    StringField(
        name='sort_on',
        required=False,
        mode='rw',
        default='sortable_title',
        widget=StringWidget(
            label=_(u'Sort the collection on this index'),
            description='',
            visible=False,
        ),
    ),

    BooleanField(
        name='sort_reversed',
        required=False,
        mode='rw',
        default=False,
        widget=BooleanWidget(
            label=_(u'Sort the results in reversed order'),
            description='',
            visible=False,
        ),
    ),

    IntegerField(
        name='b_size',
        required=False,
        mode='rw',
        default=30,
        widget=IntegerWidget(
            label=_(u'Limit Results by Page'),
            description=_(u"Specify the number of items to show by page."),
            visible=False
        ),
        validators=('isInt',)
    ),

    IntegerField(
        name='limit',
        required=False,
        mode='rw',
        default=1000000,
        widget=IntegerWidget(
            label=_(u'Limit Search Results'),
            description=_(u"Specify the maximum number of items to show."),
            visible=False
        ),
        validators=('isInt',)
    ),

    LinesField(
        name='customViewFields',
        required=False,
        mode='rw',
        default=('Title', 'Creator', 'Type', 'ModificationDate'),
        vocabulary='listMetaDataFields',
        enforceVocabulary=True,
        write_permission=ModifyPortalContent,
        widget=InAndOutWidget(
            label=_(u'Table Columns'),
            description=_(u"Select which fields to display when "
                          u"'Tabular view' is selected in the display menu."),
            visible=False
        ),
    ),
))

# Use the extended marshaller that understands queries
ReportCollectionSchema.registerLayer("marshall", CollectionRFC822Marshaller())

ReportCollectionSchema.moveField('query', after='description')

class ReportCollection(ATFolder, ObjectManager):
    """A (new style) Plone ReportCollection"""
    implements(ICollection, IReportCollection)

    meta_type = "ReportCollection"
    schema = ReportCollectionSchema

    security = ClassSecurityInfo()

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        return to_utf8(self.title)

    def listMetaDataFields(self, exclude=True):
        """Return a list of metadata fields from portal_catalog.
        """
        tool = getToolByName(self, ATCT_TOOLNAME)
        return tool.getMetadataDisplay(exclude)

    security.declareProtected(View, 'results')

    def results(self, batch=True, b_start=0, b_size=0, sort_on=None,
                brains=False, custom_query={}):
        """Get results"""
        batch_size = self.getB_size()
        if sort_on is None:
            sort_on = self.getSort_on()
        if b_size == 0 and not batch_size and not batch:
            b_size = self.getLimit()
        if b_size == 0 and batch_size and batch:
            b_size = batch_size
        print ("self.getQuery")
        return self.getQuery(batch=batch, b_start=b_start, b_size=b_size,
                             sort_on=sort_on, brains=brains,
                             custom_query=custom_query)

    def selectedViewFields(self):
        """Get which metadata field are selected"""
        _mapping = {}
        for field in self.listMetaDataFields().items():
            _mapping[field[0]] = field
        return [_mapping[field] for field in self.customViewFields]

atapi.registerType(ReportCollection, PROJECTNAME)
