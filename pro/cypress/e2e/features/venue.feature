@P0
Feature: Create and update venue

  Background:
    Given I am logged in

  Scenario: A pro user can add a venue without SIRET
    When I want to add a venue
    And I choose a venue wich already has a Siret
    And I add venue without Siret details
    And I skip offer creation
    Then I should see my venue without Siret resume

  Scenario: A pro user can add a venue with SIRET
    When I want to add a venue
    And I add a valid Siret
    And I add venue with Siret details
    And I skip offer creation
    Then I should see my venue with Siret resume

  Scenario: It should update a venue
    When I go to the venue page in Individual section
    And I update Individual section data
    Then Individual section data should be updated
    When I go to the venue page in Paramètre de l'activité
    And I update Paramètre de l'activité data
    Then Paramètre de l'activité data should be updated