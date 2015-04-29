*** Settings ***

Library          BuiltIn
Library          Selenium2Library  timeout=5  implicit_wait=0.2
Library          String
Resource         keywords.txt
Library          bika.lims.testing.Keywords
Variables        plone/app/testing/interfaces.py
Variables        bika/lims/tests/variables.py
Suite Setup      Start browser
Suite Teardown   Close All Browsers

*** Variables ***

${SITE} =           HAM
${UNIT} =           FZ1
${SHELF} =          S2

*** Test Cases ***

Test Storage Location
    Log in                      test_labmanager  test_labmanager

    Check Bika Setup imported correctly
    Create Setup Location
    Check AR Creation

*** Keywords ***

Check Bika Setup imported correctly
    Go to                       ${PLONEURL}/bika_setup/bika_storagelocations
    Wait until page contains    Storage Locations
    Page Should Contain         ${SITE}.${UNIT}.${SHELF}

Create Setup Location
    Go to                       ${PLONEURL}/bika_setup/bika_storagelocations
    Wait until page contains    Storage Locations
    Click Link                  link=Add
    Wait until page contains    Add Storage Location
    Page Should Contain         Address
    Create Location             BIKA  FR1  S3
    Go to                       ${PLONEURL}/bika_setup/bika_storagelocations
    Page should contain         BIKA.FR1.S3

Create Location
    [Arguments]  ${centre}  ${unit}  ${shelf}
    Input Text                  title  ${centre}.${unit}.${shelf}
    Input Text                  SiteTitle  BIKA Labs
    Input Text                  SiteCode  BIKA
    Input Text                  SiteDescription  BIKA Labs site in Grabou
    Input Text                  LocationTitle  Freezer ${unit}
    Input Text                  LocationCode  ${unit}
    Input Text                  LocationDescription  Freezer
    Input Text                  LocationType  Freezer
    Input Text                  ShelfTitle  Shelf ${shelf}
    Input Text                  ShelfCode  ${shelf}
    Input Text                  ShelfDescription  Second shelf from bottom
    Click Button                Save
    Wait until page contains    Changes saved.

Check AR Creation
    Go to                       ${PLONEURL}/clients/client-1
    ${ar_id}=                   Create AR
    Go to                       ${PLONEURL}/clients/client-1/${ar_id}
    Textfield Value Should Be   StorageLocation   ${SITE}.${UNIT}.${SHELF}    Storage location field is not set correctly
    Go to                       ${PLONEURL}/clients/client-1/H2O-0001
    Textfield Value Should Be   StorageLocation   ${SITE}.${UNIT}.${SHELF}    Storage location field is not set correctly

Create AR
    Click Link                          link=Add
    Wait until page contains            Request new analyses
    @{time} =                           Get Time        year month day hour min sec
    Select from dropdown                css=#Contact-0       Rita
    SelectDate                          css=#SamplingDate-0   @{time}[2]
    Select From Dropdown                css=#SampleType-0    Water
    Select from dropdown                css=#StorageLocation-0  ${SITE}.${UNIT}.${SHELF}
    click element                       css=table[form_id='lab'] th[cat='Water Chemistry']
    wait until page contains element    css=tr[title='Moisture'] td[class*='ar.0'] input[type='checkbox']
    select checkbox                     css=tr[title='Moisture'] td[class*='ar.0'] input[type='checkbox']
    click element                       css=table[form_id='lab'] th[cat='Metals']
    wait until page contains element    css=tr[title='Calcium'] td[class*='ar.0'] input[type='checkbox']
    select checkbox                     css=tr[title='Calcium'] td[class*='ar.0'] input[type='checkbox']
    select checkbox                     css=tr[title='Phosphorus'] td[class*='ar.0'] input[type='checkbox']
    click element                       css=table[form_id='lab'] th[cat='Microbiology']
    wait until page contains element    css=tr[title='Clostridia'] td[class*='ar.0'] input[type='checkbox']
    select checkbox                     css=tr[title='Clostridia'] td[class*='ar.0'] input[type='checkbox']
    select checkbox                     css=tr[title='Ecoli'] td[class*='ar.0'] input[type='checkbox']
    select checkbox                     css=tr[title='Enterococcus'] td[class*='ar.0'] input[type='checkbox']
    select checkbox                     css=tr[title='Salmonella'] td[class*='ar.0'] input[type='checkbox']
    Set Selenium Timeout                30
    Click Button                        Save
    Wait until page contains            created
    Set Selenium Timeout                10
    ${ar_id} =                          Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                          Set Variable  ${ar_id.split()[2]}
    [return]                            ${ar_id}
