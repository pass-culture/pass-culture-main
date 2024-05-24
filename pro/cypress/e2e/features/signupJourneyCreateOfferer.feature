@P0
Feature: Signup journey

  Scenario: It should create an offerer
    Given I log in with an EAC account
    When I create a new offerer with a SIRET
    Then the offerer is created

  Scenario: It should ask offerer attachment to a user and create new offerer
    Given I log in with a retention account
    When I ask for an offerer attachment
    Then the offerer is created

#   Scenario: It should attach user to an existing offerer
#     Given I log in with a retention account
#     And I click on Start
