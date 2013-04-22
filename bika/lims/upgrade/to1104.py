import logging

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.CMFCore import permissions
from bika.lims.permissions import *

from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    mp = portal.manage_permission
    mp(AddReferenceSample, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Analyst'], 1)

    mp = portal.bika_setup.bika_referencesuppliers.manage_permission
    mp(CancelAndReinstate, ['Manager', 'LabManager', 'LabClerk'], 1)
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler'], 1)
    mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
    mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst'], 1)
    portal.bika_setup.bika_referencesuppliers.reindexObject()

    return True
