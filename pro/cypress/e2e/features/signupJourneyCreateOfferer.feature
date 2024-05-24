@P0
Feature: Signup journey

  Scenario: With a new account, create a new offerer with an unknown SIRET
    Given I log in with a "first" new account
    When I start offerer creation
    And I specify an offerer with a SIRET
    And I add details to offerer
    And I fill activity step
    And I validate
    Then the offerer is created

  Scenario: With a new account and a known offerer, create a new offerer in the space
    Given I log in with a "second" new account
    When I start offerer creation
    And I specify an offerer with a SIRET
    And I add a new offerer
    And I fill identification step
    And I fill activity step
    And I validate
    Then the offerer is created

  Scenario: With a new account and a known offerer, ask to join space
    Given I log in with a "third" new account
    When I start offerer creation
    And I specify an offerer with a SIRET
    And I chose to join the space
    Then I am redirected to homepage
    And the attachment is in progress
