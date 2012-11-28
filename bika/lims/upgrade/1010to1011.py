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

    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'controlpanel')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'factorytool')

    # Changes to the catalogs
    c = getToolByName(portal, 'bika_patient_catalog')
    c.delIndex('getPatientID')
    c.addIndex('getPatientID', 'FieldIndex')
    logger.info("Rebuilding patient catalog")
    c.clearFindAndRebuild()

    # IdentifierTypes
    logger.info("add bika_identifiertypes")
    bs = portal.bika_setup
    if 'bika_identifiertypes' not in bs.objectIds():
        typestool.constructContent(type_name="IdentifierTypes",
                                   container=bs,
                                   id='bika_identifiertypes',
                                   title='Identifier Types')
        obj = bs['bika_identifiertypes']
        obj.unmarkCreationFlag()
        obj.reindexObject()

    # / folder permissions
    mp = portal.manage_permission
    mp(permissions.ListFolderContents, ['Authenticated'], 1)
    mp(permissions.View, ['Anonymous'], 1)
    mp('Access contents information', ['Anonymous'], 1)

    mp = portal.patients.manage_permission
    mp(CancelAndReinstate, ['Manager', 'LabManager', 'Doctor', ], 1)
    mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Doctor', 'Analyst', 'Sampler', 'Preserver', 'Owner'], 1)
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'LabTechnician', 'Doctor', 'Owner', 'Sampler', 'Preserver'], 1)
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'LabTechnician', 'Doctor', 'Owner', 'Sampler', 'Preserver'], 1)

    return True
