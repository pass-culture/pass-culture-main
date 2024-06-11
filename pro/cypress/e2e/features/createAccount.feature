@P0
Feature: Account creation

  Scenario: It should create an account
    Given I open the "inscription" page
    When I fill required information in create account form
    And I submit
    Then my account should be created
