from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.ZCatalog.ZCatalog import ZCatalog
from zope.interface import implements


def getCatalog(instance, field='UID'):
    """ Return the catalog which indexes objects of instance's type.
    If an object is indexed by more than one catalog, the first match
    will be returned.
    """
    uid = instance.UID()
    if 'workflow_skiplist' in instance.REQUEST and \
        [x for x in instance.REQUEST['workflow_skiplist']
         if x.find(uid) > -1]:
        return None
    else:
        # grab the first catalog we are indexed in.
        # we're only indexed in one.
        at = getToolByName(instance, 'archetype_tool')
        plone = instance.portal_url.getPortalObject()
        catalog_name = instance.portal_type in at.catalog_map \
            and at.catalog_map[instance.portal_type][0] or 'portal_catalog'
        catalog = getToolByName(plone, catalog_name)
        return catalog

