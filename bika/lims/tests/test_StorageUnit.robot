*** Settings ***

Library         BuiltIn
Library         Selenium2Library  timeout=5  implicit_wait=0.2
Library         String
Resource        keywords.txt
Library         bika.lims.testing.Keywords
Resource        plone/app/robotframework/selenium.robot
Library         Remote  ${PLONEURL}/RobotRemote
Variables       plone/app/testing/interfaces.py
Variables       bika/lims/tests/variables.py

Suite Setup     Start browser
Suite Teardown  Close All Browsers

Library          DebugLibrary

*** Variables ***

*** Test Cases ***

Test StorageUnit as LabManager
    Log in  test_labmanager  test_labmanager
    Set separator in inventory tab of bika setup

    When I add Freezer as storage unit
     and I add 5 storage levels in Freezer with title Drawer
    Then page should contain  Drawer-1
     and page should contain  Drawer-5

    When I add 30 storage levels with title Shelf in Drawer-1 of Freezer
    Then page should contain  Shelf-1
     and pages should be batched
     and the unit Freezer should not have Shelf-1

*** Keywords ***

# --- When ------------------------------------------------------------------

I Add ${title} as storage unit
    go to  ${PLONEURL}/bika_setup/bika_storageunits/portal_factory/StorageUnit/xxx/edit
    wait until page contains  xxx
    input text  css=#title  ${title}
    # Alphabets are not allowed in temperature
    input text  css=#Temperature  asdf-80
    click button  Save
    wait until page contains  saved

I Add ${number} storage levels in ${storageunit} with title ${title}
    go to  ${PLONEURL}/bika_setup/bika_storageunits/
    click link  ${storageunit}
    input text  css=.storagelevel-title  ${title}
    input text  css=.storagelevel-number  ${number}
    click button  Add storage levels
    wait until page contains  saved

I add ${number} storage levels with title ${title} in ${storagelevel} of ${storageunit}
    go to  ${PLONEURL}/bika_setup/bika_storageunits/
    click link  ${storageunit}
    click link  ${storagelevel}
    input text  css=.storagelevel-title  ${title}
    input text  css=.storagelevel-number  ${number}
    click button  Add storage levels
    wait until page contains  saved

# --- Then ------------------------------------------------------------------

the unit ${storageunit} should not have ${storagelevel}
    go to  ${PLONEURL}/bika_setup/bika_storageunits/
    click link  ${storageunit}
    page should not contain  ${storagelevel}

# --- other ------------------------------------------------------------------

Set separator in inventory tab of bika setup
    go to  ${PLONEURL}/bika_setup/edit
    click link  Inventory
    select from list  css=#StorageLevelTitleSeparator  -
    click button  Save
    wait until page contains  saved

pages should be batched
    # page is made into batches of 25 if more elements are listed
    page should contain  Items per page
