import logging

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.CMFCore import permissions
from bika.lims.permissions import *

from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """ Create bika_identifiertypes
    """
    logger = logging.getLogger('Bika 1010to1011')
    portal = aq_parent(aq_inner(tool))
    portal_catalog = getToolByName(portal, 'portal_catalog')
    typestool = getToolByName(portal, 'portal_types')
    workflowtool = getToolByName(portal, 'portal_workflow')
    setup = portal.portal_setup

    # / folder permissions
    mp = portal.manage_permission
    mp(AddAetiologicAgent, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Doctor'], 1)

    return True
