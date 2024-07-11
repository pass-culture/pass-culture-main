@P10 @retries(runMode=0)
Feature: Signup journey

  Background:
    Given pro user new nav has been created
    And I am logged in with an empty account

  Scenario: With a new account, create a new offerer with an unknown SIRET
    When I start offerer creation
    And I specify an offerer with a SIRET
    And I fill identification form with a public name
    And I fill activity form without target audience
    Then An error message is raised
    When I fill in missing target audience
    Then The next step is displayed
    When I validate the registration
    Then the offerer is created

  Scenario: With a new account and a known offerer, create a new offerer in the space
    When individual offers has been created
    And I start offerer creation
    And I specify an offerer with a SIRET
    And I add a new offerer
    And I fill identification form with a new address
    And I fill activity form without main activity
    Then An error message is raised
    When I fill in missing main activity
    Then The next step is displayed
    When I validate the registration
    Then the offerer is created
    And the attachment is in progress

  Scenario: With a new account and a known offerer, ask to join space
    When individual offers has been created
    And I start offerer creation
    And I specify an offerer with a SIRET
    And I chose to join the space
    Then I am redirected to homepage
    And the attachment is in progress
