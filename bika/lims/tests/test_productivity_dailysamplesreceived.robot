*** Settings ***

Library         BuiltIn
Library         Selenium2Library  timeout=5  implicit_wait=0.2
Library         String
Resource        keywords_analysisrequest.txt
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

Create Report
    [Documentation]   Create report as Lab Manager user.
    ...  Should be able to report on all samples from all clients.
    Enable autologin as   LabManager
    Simple AR Creation   client-1  Rita     Water   Metals   Zinc
    Simple AR Creation   client-2  Johanna  Water   Metals   Zinc

    # We'll make a report with the default parameters
    go to  ${PLONEURL}/reports
    Click Link  css=dl#bika-reports-productivity dt.actionMenuHeader a
    Click Link  css=a#dailysamplesreceived
    wait until page contains    Search terms
    click button     Save

    # After save, the report template should be displayed.
    # There should be two Zinc analyses, one from each AR.
    debug
    wait until page contains        asdf
    xpath should match x times       2

    Debug



*** Keywords ***

a new Daily Samples Received report in Productivity category
    go to   ${PLONEURL}/reports
    debug
    click element   asdf
