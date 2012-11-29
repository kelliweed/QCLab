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
    portal = aq_parent(aq_inner(tool))
    portal_catalog = getToolByName(portal, 'portal_catalog')
    typestool = getToolByName(portal, 'portal_types')
    workflowtool = getToolByName(portal, 'portal_workflow')
    setup = portal.portal_setup


    # / folder permissions
    mp = portal.manage_permission
    mp(AddAetiologicAgent, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Doctor'], 1)
    mp(AddTreatment, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Doctor'], 1)
    mp(AddDrug, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Doctor'], 1)
    mp(AddImmunization, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Doctor'], 1)
    mp(AddVaccinationCenter, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Doctor'], 1)
    mp(AddSymptom, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Doctor'], 1)
    mp(AddDrugProhibition, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Doctor'], 1)

    return True
