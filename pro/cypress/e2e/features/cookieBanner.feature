@P0
Feature: Cookie management

  Scenario: The cookie banner should remain displayed when opening a new page
    Given I open the "connexion" page
    When I decline all cookies
    And I clear all cookies in Browser
    And I click on the "Accessibilité : non conforme" link
    Then The cookie banner should be displayed

  Scenario: The user can accept all, and all the cookies are checked in the dialog
    Given I open the "connexion" page
    Then The cookie banner should be displayed
    When I accept all cookies
    Then The cookie banner should not be displayed
    When I open the cookie management option
    Then I should have 4 items checked

  Scenario: The user can refuse all, and no cookie is checked in the dialog, except the required
    Given I open the "connexion" page
    When I decline all cookies
    Then The cookie banner should not be displayed
    When I open the cookie management option
    Then I should have 1 items checked

  Scenario: The user can choose a specific cookie, save and the status should be the same on modal re display
    Given I open the "connexion" page
    When I open the choose cookies option
    And I select the "Beamer" cookie
    And I save my choices
    And I open the cookie management option
    Then The Beamer cookie should be checked

  Scenario: The user can choose a specific cookie, reload the page and the status should not have been changed
    Given I open the "connexion" page
    When I open the choose cookies option
    And I select the "Beamer" cookie
    And I open the "connexion" page
    And I open the choose cookies option
    Then The Beamer cookie should not be checked

  Scenario: The user can choose a specific cookie, close the modal and the status should not have been changed
    Given I open the "connexion" page
    When I open the choose cookies option
    And I select the "Beamer" cookie
    And I close the cookie option
    And I open the choose cookies option
    Then The Beamer cookie should be checked

  Scenario: The user can choose a specific cookie, log in with another account and check that specific cookie is checked
    Given I clear all cookies in Browser
    And I am logged in with account 1
    When I open the cookie management option
    And I select the "Beamer" cookie
    And I save my choices
    When I disconnect of my account
    And I am logged in with account 2 and no cookie selection
    And I open the cookie management option
    Then The Beamer cookie should be checked

  Scenario: The user log in, choose a specific cookie, open another browser, log in again and check that specific cookie not checked
    # Cypress cannot deal with 2 browsers or a tab. So we log out, and log in again with a clean browser
    # See https://docs.cypress.io/guides/references/trade-offs#Multiple-browsers-open-at-the-same-time
    Given I clear all cookies in Browser
    And I am logged in with account 1
    When I open the cookie management option
    And I select the "Beamer" cookie
    And I save my choices
    When I disconnect of my account
    And I clear all cookies and storage
    And I am logged in with account 1
    And I open the cookie management option
    Then The Beamer cookie should not be checked
