*** Settings ***
Library    SeleniumLibrary
Library    helper.py
Library    Collections

Suite Setup    Setup Browser
Suite Teardown    Close All Browsers

*** Variables ***
${REPORT_FILE}      report.html
${PARQUET_FOLDER}   ${CURDIR}/parquet_data
${FILTER_DATE}      2025-10-29
${BROWSER}          chrome

*** Keywords ***
Setup Browser
    Open Browser    about:blank    ${BROWSER}
    Maximize Browser Window

*** Test Cases ***
Test 1: Exact Data Comparison
    # Open the report
    Go To    file://${CURDIR}/${REPORT_FILE}
    Wait Until Page Contains Element    class:table    10s

    ${html_df}=    Read Html Table To Dataframe    ${REPORT_FILE}    ${FILTER_DATE}
    ${parquet_df}=    Read Parquet To Dataframe    ${PARQUET_FOLDER}    ${FILTER_DATE}

    ${are_equal}    ${message}=    Compare Dataframes    ${html_df}    ${parquet_df}

    Run Keyword If    ${are_equal}
    ...    Log    ✓ Test 1 PASSED: ${message}
    ...    ELSE
    ...    Fail    ✗ Test 1 FAILED: ${message}

Test 2: DQE - Compare Row Counts
    ${html_df}=    Read Html Table To Dataframe    ${REPORT_FILE}    ${FILTER_DATE}
    ${parquet_df}=    Read Parquet To Dataframe    ${PARQUET_FOLDER}    ${FILTER_DATE}

    ${html_rows}=    Get Row Count    ${html_df}
    ${parquet_rows}=    Get Row Count    ${parquet_df}

    Should Be Equal As Integers    ${html_rows}    ${parquet_rows}
    ...    Row count mismatch: HTML has ${html_rows} rows, Parquet has ${parquet_rows} rows

Test 3: DQE - Compare Column Counts
    ${html_df}=    Read Html Table To Dataframe    ${REPORT_FILE}    ${FILTER_DATE}
    ${parquet_df}=    Read Parquet To Dataframe    ${PARQUET_FOLDER}    ${FILTER_DATE}

    ${html_cols}=    Get Column Count    ${html_df}
    ${parquet_cols}=    Get Column Count    ${parquet_df}

    Should Be Equal As Integers    ${html_cols}    ${parquet_cols}
    ...    Column count mismatch: HTML has ${html_cols} columns, Parquet has ${parquet_cols} columns

Test 4: DQE - Compare Facility Type Distribution
    ${html_df}=    Read Html Table To Dataframe    ${REPORT_FILE}    ${FILTER_DATE}
    ${parquet_df}=    Read Parquet To Dataframe    ${PARQUET_FOLDER}    ${FILTER_DATE}

    ${html_counts}=    Get Facility Type Counts    ${html_df}
    ${parquet_counts}=    Get Facility Type Counts    ${parquet_df}

    Dictionaries Should Be Equal    ${html_counts}    ${parquet_counts}
    ...    Facility Type distribution mismatch: HTML: ${html_counts}, Parquet: ${parquet_counts}

Test 5: DQE - Compare Visit Date Distribution
    ${html_df}=    Read Html Table To Dataframe    ${REPORT_FILE}    ${FILTER_DATE}
    ${parquet_df}=    Read Parquet To Dataframe    ${PARQUET_FOLDER}    ${FILTER_DATE}

    ${html_counts}=    Get Visit Date Counts    ${html_df}
    ${parquet_counts}=    Get Visit Date Counts    ${parquet_df}

    Dictionaries Should Be Equal    ${html_counts}    ${parquet_counts}
    ...    Visit Date distribution mismatch: HTML: ${html_counts}, Parquet: ${parquet_counts}

Test 6: DQE - Compare Average Time Spent Statistics
    ${html_df}=    Read Html Table To Dataframe    ${REPORT_FILE}    ${FILTER_DATE}
    ${parquet_df}=    Read Parquet To Dataframe    ${PARQUET_FOLDER}    ${FILTER_DATE}

    ${html_stats}=    Get Average Time Stats    ${html_df}
    ${parquet_stats}=    Get Average Time Stats    ${parquet_df}

    ${html_mean}=    Set Variable    ${html_stats}[mean]
    ${parquet_mean}=    Set Variable    ${parquet_stats}[mean]
    Should Be Equal As Numbers    ${html_mean}    ${parquet_mean}    0.01
    ...    Average Time Spent mean mismatch: HTML=${html_mean}, Parquet=${parquet_mean}

    ${html_sum}=    Set Variable    ${html_stats}[sum]
    ${parquet_sum}=    Set Variable    ${parquet_stats}[sum]
    Should Be Equal As Numbers    ${html_sum}    ${parquet_sum}    0.01
    ...    Total Time Spent mismatch: HTML=${html_sum}, Parquet=${parquet_sum}

Test 7: DQE - Compare Missing Values
    ${html_df}=    Read Html Table To Dataframe    ${REPORT_FILE}    ${FILTER_DATE}
    ${parquet_df}=    Read Parquet To Dataframe    ${PARQUET_FOLDER}    ${FILTER_DATE}

    ${html_missing}=    Get Missing Value Count    ${html_df}
    ${parquet_missing}=    Get Missing Value Count    ${parquet_df}

    Should Be Equal As Integers    ${html_missing}    ${parquet_missing}
    ...    Missing value count mismatch: HTML has ${html_missing}, Parquet has ${parquet_missing}