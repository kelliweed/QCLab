# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.


from bika.lims.content.analysis import Analysis
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.utils import tmpID
from bika.lims.utils.analysisrequest import create_analysisrequest
from bika.lims.workflow import doActionFor
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
import unittest

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class Test_LIMS2001(BikaFunctionalTestCase):
    """
    When adding a duplicate for an AR in a worksheet, only the first analysis
    gets duplicated: https://jira.bikalabs.com/browse/LIMS-2001
    """
    layer = BIKA_FUNCTIONAL_TESTING

    def setUp(self):
        super(Test_LIMS2001, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def tearDown(self):
        logout()
        super(Test_LIMS2001, self).tearDown()

    def test_LIMS2001(self):
        # ARs creation
        # Client:       Happy Hills
        # SampleType:   Apple Pulp
        # Contact:      Rita Mohale
        client = self.portal.clients['client-1']
        sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
        values = {'Client': client.UID(),
                  'Contact': client.getContacts()[0].UID(),
                  'SamplingDate': '2015-01-01',
                  'SampleType': sampletype.UID()}
        # analysis-service-3: Calcium (Ca)
        # analysis-service-6: Cooper (Cu)
        # analysis-service-7: Iron (Fe)
        servs = self.portal.bika_setup.bika_analysisservices
        aservs = [servs['analysisservice-3'],
                  servs['analysisservice-6'],
                  servs['analysisservice-7']]
        services = [s.UID() for s in aservs]
        request = {}
        ar = create_analysisrequest(client, request, values, services)
        sp = _createObjectByType('SamplePartition', ar.getSample(), tmpID())
        wf = getToolByName(ar, 'portal_workflow')
        wf.doActionFor(ar, 'receive')

        # Worksheet creation
        wsfolder = self.portal.worksheets
        ws = _createObjectByType("Worksheet", wsfolder, tmpID())
        ws.processForm()
        bsc = getToolByName(self.portal, 'bika_setup_catalog')
        lab_contacts = [o.getObject() for o in bsc(portal_type="LabContact")]
        lab_contact = [o for o in lab_contacts if o.getUsername() == 'analyst1']
        self.assertEquals(len(lab_contact), 1)
        lab_contact = lab_contact[0]
        ws.setAnalyst(lab_contact)
        ws.setResultsLayout(self.portal.bika_setup.getWorksheetLayout())
        # Add analyses into the worksheet
        self.request['context_uid'] = ws.UID()
        for analysis in ar.getAnalyses():
            an = analysis.getObject()
            an.setSamplePartition(sp)
            ws.addAnalysis(an)
        self.assertEquals(len(ws.getAnalyses()), 3)

        # Add a duplicate for slot 1 (there's only one slot)
        ws.addDuplicateAnalyses('1', None)
        ans = ws.getAnalyses()
        reg = [an for an in ans if an.portal_type == 'Analysis']
        dup = [an for an in ans if an.portal_type == 'DuplicateAnalysis']
        regkeys = [an.getKeyword() for an in reg]
        dupkeys = [an.getKeyword() for an in dup]
        regkeys.sort()
        dupkeys.sort()
        expregs = ['Ca', 'Cu', 'Fe']
        expdups = ['Ca', 'Cu', 'Fe']
        self.assertEquals(regkeys, expregs)
        self.assertEquals(dupkeys, expdups)

        # Add a result, submit and add another duplicate
        an1 = [an for an in reg if an.getKeyword() == 'Cu'][0]
        an1.setResult('13')
        wf.doActionFor(an1, 'submit')
        ws.addDuplicateAnalyses('1', None)
        ans = ws.getAnalyses()
        reg = [an for an in ans if an.portal_type == 'Analysis']
        dup = [an for an in ans if an.portal_type == 'DuplicateAnalysis']
        regkeys = [an.getKeyword() for an in reg]
        dupkeys = [an.getKeyword() for an in dup]
        regkeys.sort()
        dupkeys.sort()
        expregs = ['Ca', 'Cu', 'Fe']
        expdups = ['Ca', 'Ca', 'Cu', 'Cu', 'Fe', 'Fe']
        self.assertEquals(regkeys, expregs)
        self.assertEquals(dupkeys, expdups)

        # Retract the previous analysis and add another duplicate
        wf.doActionFor(an1, 'retract')
        ws.addDuplicateAnalyses('1', None)
        ans = ws.getAnalyses()
        reg = [an for an in ans if an.portal_type == 'Analysis']
        dup = [an for an in ans if an.portal_type == 'DuplicateAnalysis']
        regkeys = [an.getKeyword() for an in reg]
        dupkeys = [an.getKeyword() for an in dup]
        regkeys.sort()
        dupkeys.sort()
        expregs = ['Ca', 'Cu', 'Cu', 'Fe']
        expdups = ['Ca', 'Ca', 'Ca', 'Cu', 'Cu', 'Cu', 'Fe', 'Fe', 'Fe']
        self.assertEquals(regkeys, expregs)
        self.assertEquals(dupkeys, expdups)

        # Do the same process, but with two ARs
        ar = create_analysisrequest(client, request, values, services)
        sp = _createObjectByType('SamplePartition', ar.getSample(), tmpID())
        wf.doActionFor(ar, 'receive')
        # Add analyses into the worksheet
        for analysis in ar.getAnalyses():
            an = analysis.getObject()
            an.setSamplePartition(sp)
            ws.addAnalysis(an)
        ans = ws.getAnalyses()
        reg = [an for an in ans if an.portal_type == 'Analysis']
        regkeys = [an.getKeyword() for an in reg]
        regkeys.sort()
        expregs = ['Ca', 'Ca', 'Cu', 'Cu', 'Cu', 'Fe', 'Fe']
        self.assertEquals(regkeys, expregs)

        # Add a duplicte for the second AR
        # slot 1: previous AR
        # slot 2: Duplicate 1 (analysis without result)
        # slot 3: Duplicate 2 (analysis with submitted result)
        # slot 4: Duplicate 3 (analysis retracted)
        # slot 5: this new AR
        ws.addDuplicateAnalyses('5', None)
        ans = ws.getAnalyses()
        reg = [an for an in ans if an.portal_type == 'Analysis']
        dup = [an for an in ans if an.portal_type == 'DuplicateAnalysis']
        regkeys = [an.getKeyword() for an in reg]
        dupkeys = [an.getKeyword() for an in dup]
        regkeys.sort()
        dupkeys.sort()
        expregs = ['Ca', 'Ca', 'Cu', 'Cu', 'Cu', 'Fe', 'Fe']
        expdups = ['Ca', 'Ca', 'Ca', 'Ca',
                   'Cu', 'Cu', 'Cu', 'Cu',
                   'Fe', 'Fe', 'Fe', 'Fe']
        self.assertEquals(regkeys, expregs)
        self.assertEquals(dupkeys, expdups)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_LIMS2001))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
