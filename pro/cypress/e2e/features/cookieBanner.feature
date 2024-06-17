@P0
Feature: Cookie management

  Background:
    Given I open the "connexion" page

  Scenario: The cookie banner should be displayed on cookie deletion
    When I decline all cookies
    And I clear all cookies in Browser
    And I open the "connexion" page
    Then The cookie banner should be displayed

  Scenario: The user can accept all, and all the cookies are checked in the dialog
    Then The cookie banner should be displayed
    When I accept all cookies
    Then The cookie banner should not be displayed
    When I open the cookie management option
    Then I should have 4 items checked

  Scenario: The user can refuse all, and no cookie is checked in the dialog, except the required
    When I decline all cookies
    Then The cookie banner should not be displayed
    When I open the cookie management option
    Then I should have 1 items checked

  Scenario: The user can choose a specific cookie, save and the status should be the same on modal re display
    When I open the choose cookies option
    And I select the "Beamer" cookie
    And I save my choices
    And I open the cookie management option
    Then The Beamer cookie should be checked

  Scenario: The user can choose a specific cookie, reload the page and the status should not have been changed
    When I open the choose cookies option
    And I select the "Beamer" cookie
    And I open the "connexion" page
    And I open the choose cookies option
    Then The Beamer cookie should not be checked

  Scenario: The user can choose a specific cookie, close the modal and the status should not have been changed
    When I open the choose cookies option
    And I select the "Beamer" cookie
    And I close the cookie option
    And I open the choose cookies option
    Then The Beamer cookie should be checked
