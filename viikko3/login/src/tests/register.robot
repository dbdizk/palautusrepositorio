*** Settings ***
Resource  resource.robot
Suite Setup     Open And Configure Browser
Suite Teardown  Close Browser
Test Setup      Reset Application Create User And Go To Register Page

*** Test Cases ***
Register With Valid Username And Password
    Set Username  testi1
    Set Password  testi1234
    Set Confirmation  testi1234
    Click Button  Register
    Register Should Succeed

Register With Too Short Username And Valid Password
    Set Username  te
    Set Password  testi1234
    Set Confirmation  testi1234
    Click Button  Register
    Register Should Fail With Message  Username must be at least 3 characters
Register With Valid Username And Too Short Password
    Set Username  testi1
    Set Password  testi12
    Set Confirmation  testi12
    Click Button  Register
    Register Should Fail With Message  Password too short

Register With Valid Username And Invalid Password
    Set Username  testi1
    Set Password  testitesti
    Set Confirmation  testitesti
    Click Button  Register
    Register Should Fail With Message  Invalid password, cannot contain only letters

Register With Nonmatching Password And Password Confirmation
    Set Username  testi1
    Set Password  testi123
    Set Confirmation  testi1234
    Click Button  Register
    Register Should Fail With Message  Passwords don't match

Register With Username That Is Already In Use
    Set Username  kalle
    Set Password  testi333
    Set Confirmation  testi333
    Click Button  Register
    Register Should Fail With Message  User with username kalle already exists


*** Keywords ***
Reset Application Create User And Go To Register Page
    Reset Application
    Create User  kalle  kalle123
    Go To Register Page

Register Should Succeed
    Welcome Page Should Be Open

Register Should Fail With Message
    [Arguments]  ${message}
    Register Page Should Be Open
    Page Should Contain  ${message}

Set Username
    [Arguments]  ${username}
    Input Text  username  ${username}

Set Password
    [Arguments]  ${password}
    Input Password  password  ${password}

Set Confirmation
    [Arguments]  ${password}
    Input Password  password_confirmation  ${password}    
