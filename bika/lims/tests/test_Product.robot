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

Test Product as LabManager
    Log in  test_labmanager  test_labmanager

    Choose to categorise products in bika setup
    Add Sampling Kit as product category
    Add Kit Component as product category

    Given a blank product form in supplier-1
     When I enter the title Water-sampling kit
      and I select the category Sampling Kit
      and I enter other fields
      and I submit the form
     Then products list of supplier-1 should contain Water-sampling kit under Sampling Kit

    Given a blank product form in supplier-1
     When I enter the title Ziplock bag
      and I select the category Kit Component
      and I submit the form
     Then products list of supplier-1 should contain Ziplock bag under Kit Component
      and page should not contain  Water-sampling kit

    Given a blank product form in supplier-2
     When I enter the title Test tube
      and I select the category Kit Component
      and I submit the form
     Then products list of supplier-2 should contain Test tube under Kit Component
      and products list of supplier-1 should not contain Test tube under Kit Component


Test StockItem as LabManager
    Log in  test_labmanager  test_labmanager

    Add Sampling Kit as product category
    Add Water-sampling kit as product under Sampling Kit in supplier-1

    Given a blank stock item form
     When I select the product Water-sampling kit
      and I enter other fields of the item
      and I submit the form
     Then stock items list should contain Water-sampling kit and Sampling Kit


*** Keywords ***

# --- Given ------------------------------------------------------------------

a blank product form in ${supplier}
    [Documentation]  Load a fresh Product form
    go to  ${PLONEURL}/bika_setup/bika_suppliers/${supplier}/portal_factory/Product/xxx/edit
    wait until page contains  xxx

a blank stock item form
    [Documentation]  Load a fresh Stock item form
    go to  ${PLONEURL}/bika_setup/bika_stockitems/portal_factory/StockItem/xxx/edit
    wait until page contains  xxx

# --- When ------------------------------------------------------------------

I enter the title ${title}
    [Documentation]  Input the title for the product
    input text  css=#title  ${title}

I select the category ${category}
    [Documentation]  Input the product category for the product
    select from list  xpath=//select[contains(@id, 'Category:list')]  ${category}


I enter other fields
    [Documentation]  Fill other fields while adding Product
    input text  css=#CAS  124124
    select checkbox  css=#Hazardous
    input text  css=#Quantity  4
    input text  css=#Unit  no.
    click link  Price
    input text  css=#VAT  5.60
    input text  css=#Price  149.99

I submit the form
    [Documentation]  Save the form and wait for the submission to complete
    click button  Save
    wait until page contains  saved

I select the product ${product}
    select from dropdown  css=#Product  ${Product}

I enter other fields of the item
    input text  css=#dateReceived  2015-06-19
    input text  css=#location  Winterfell

# --- Then ------------------------------------------------------------------

products list of ${supplier} should contain ${title} under ${category}
    go to  ${PLONEURL}/bika_setup/bika_suppliers/${supplier}/products
    click element  xpath=//th[contains(@cat, '${category}')]
    page should contain  ${title}

products list of ${supplier} should not contain ${title} under ${category}
    go to  ${PLONEURL}/bika_setup/bika_suppliers/${supplier}/products
    click element  xpath=//th[contains(@cat, '${category}')]
    page should not contain  ${title}

stock items list should contain ${product} and ${category}
    go to  ${PLONEURL}/bika_setup/bika_stockitems
    wait until page contains  Stock items
    page should contain  ${product}
    page should contain  ${category}

# --- other ------------------------------------------------------------------

Choose to categorise products in bika setup
    go to  ${PLONEURL}/bika_setup/
    click link  Inventory
    select checkbox  css=#CategoriseProducts
    click button  Save
    wait until page contains  saved

Add ${categoryName} as product category
    go to  ${PLONEURL}/bika_setup/bika_productcategories/portal_factory/ProductCategory/xxx/edit
    wait until page contains  xxx
    input text  css=#title  ${categoryName}
    click button  Save
    wait until page contains  saved

Add ${title} as product under ${category} in ${supplier}
    go to  ${PLONEURL}/bika_setup/bika_suppliers/${supplier}/portal_factory/Product/xxx/edit
    wait until page contains  xxx
    input text  css=#title  ${title}
    select from list  xpath=//select[contains(@id, 'Category:list')]  ${category}
    click button  Save
    wait until page contains  saved
