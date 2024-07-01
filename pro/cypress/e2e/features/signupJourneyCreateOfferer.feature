@P0 @retries(runMode=0)
Feature: Signup journey

  Scenario: With a new account, create a new offerer with an unknown SIRET
    Given I log in with a new account
    When I start offerer creation
    And I specify an offerer with a SIRET
    And I add details to offerer
    And I fill activity form without target audience
    Then An error message is raised
    When I fill in missing target audience
    Then The next step is displayed
    When I validate the registration
    Then the offerer is created

  Scenario: With a new account and a known offerer, create a new offerer in the space
    Given I create a user offerer
    Given I log in with a new account
    When I start offerer creation
    And I specify an offerer with a SIRET
    And I add a new offerer
    And I fill identification step
    And I fill activity form without main activity
    Then An error message is raised
    When I fill in missing main activity
    Then The next step is displayed
    When I validate the registration
    Then the offerer is created
    And the attachment is in progress

  Scenario: With a new account and a known offerer, ask to join space
    Given I log in with a new account
    When I start offerer creation
    And I specify an offerer with a SIRET
    And I chose to join the space
    Then I am redirected to homepage
    And the attachment is in progress
