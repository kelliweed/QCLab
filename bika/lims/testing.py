from Products.CMFCore.utils import getToolByName
from Testing.makerequest import makerequest
from bika.lims.exportimport.load_setup_data import LoadSetupData
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.testing import Layer
from plone.testing import z2
import Products.ATExtensions
import Products.PloneTestCase.setup
import bika.lims
import collective.js.jqueryui
import plone.app.iterate

class BikaTestLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        self.loadZCML(package=Products.ATExtensions)
        self.loadZCML(package=plone.app.iterate)
        self.loadZCML(package=collective.js.jqueryui)
        self.loadZCML(package=bika.lims)

        # Required by Products.CMFPlone:plone-content
        z2.installProduct(app, 'Products.PythonScripts')
        z2.installProduct(app, 'bika.lims')

        # Install product and call its initialize() function
        z2.installProduct(app, 'bika.lims')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'bika.lims:default')

        login(portal, TEST_USER_NAME)
        setRoles(portal, TEST_USER_ID, ['Member', 'Manager',])
        self.request = makerequest(portal.aq_parent).REQUEST

        # initialise skins support
        portal.clearCurrentSkin()
        portal.setupCurrentSkin(self.request)
        Products.PloneTestCase.setup._placefulSetUp(portal)

        self.applyProfile(portal, 'bika.lims:default')

        # Add some test users
        for role in ('LabManager',
                     'LabClerk',
                     'Analyst',
                     'Verifier',
                     'Sampler',
                     'Preserver',
                     'Publisher',
                     'Member',
                     'Reviewer',
                     'RegulatoryInspector'):
            for user_nr in range(2):
                if user_nr == 0:
                    username = "test_%s" % (role.lower())
                else:
                    username = "test_%s%s" % (role.lower(), user_nr)
                member = portal.portal_registration.addMember(
                    username,
                    username,
                    properties={
                        'username': username,
                        'email': username + "@example.com",
                        'fullname': username}
                )
                # Add user to all specified groups
                group_id = role + "s"
                group = portal.portal_groups.getGroupById(group_id)
                if group:
                    group.addMember(username)
                # Add user to all specified roles
                member._addRole(role)
                # If user is in LabManagers, add Owner local role on clients folder
                if role == 'LabManager':
                    portal.clients.manage_setLocalRoles(username, ['Owner', ])

        self.request.form['setupexisting'] = 1
        self.request.form['existing'] = "test"
        lsd = LoadSetupData(portal, self.request)
        lsd()

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'bika.lims')

BIKA_FIXTURE = BikaTestLayer()
BIKA_INTEGRATION_TESTING = IntegrationTesting(bases=(BIKA_FIXTURE,), name="BikaIntegrationTesting")
BIKA_FUNCTIONAL_TESTING = FunctionalTesting(bases=(BIKA_FIXTURE,), name="BikaFunctionalTesting")
BIKA_ROBOT_TESTING = FunctionalTesting(bases=(BIKA_WINE_FIXTURE, z2.ZSERVER_FIXTURE), name="BikaTestingLayer:Robot")
