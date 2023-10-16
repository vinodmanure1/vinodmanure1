*** Settings ***
Documentation  Login Functionality
Library  SeleniumLibrary



*** Variables ***
${URL}            https://www.saucedemo.com/
${BROWSER}        Edge
${WAIT_TIME}      10s
${USERNAME}       standard_user
${PASSWORD}       secret_sauce

*** Test Cases ***
Test Swag Labs Website
    Open Browser    ${URL}    ${BROWSER}
    Maximize Browser Window
    Title Should Be    Swag Labs
    Input Text    id=user-name    ${USERNAME}
    Input Text    id=password    ${PASSWORD}
    Click Button    class=btn_action
    Location Should Be    ${URL}inventory.html
    Input Text    id=user-name    invalid_username
    Input Text    id=password    ${PASSWORD}
    Click Button    class=btn_action
    Wait Until Element Is Visible    xpath=//h3[@data-test='error']   ${WAIT_TIME}

*** Keywords ***
Unsuccessful Login with Invalid Password
   Input Text   id=user-name   ${USERNAME}
   Input Text   id=password   invalid_password
   Click Button   class=btn_action
   Wait Until Element Is Visible  xpath=//h3[@data-test='error']  ${WAIT_TIME}

Logout And Verify
   Click Element   id=react-burger-menu-btn
   Click Element   id=logout_sidebar_link
   Location Should Be   ${URL}index.html

Add To Cart And Verify
   Input Text   id=user-name   ${USERNAME}
   Input Text   id=password   ${PASSWORD}
   Click Button   class=btn_action
   Click Element   id=add-to-cart-sauce-labs-backpack
   Click Element   class=shopping_cart_link
   Wait Until Element Is Visible  class=inventory_item_name  ${WAIT_TIME}

Remove From Cart And Verify
   Click Element  id=remove-sauce-labs-backpack

Proceed To Checkout And Verify
   Input Text  id=user-name  ${USERNAME}
   Input Text  id=password  ${PASSWORD}
   Click Button  class=btn_action
   Click Element  id=add-to-cart-sauce-labs-backpack
   Click Element  class=shopping_cart_link
   Wait Until Element Is Visible  class=inventory_item_name  ${WAIT_TIME}

Enter Shipping Information And Verify
   Input Text  id=first-name  John
   Input Text  id=last-name  Doe
   Input Text  id=postal-code  12345

Enter Payment Information And Place Order And Verify
   Click Button  id=finish
