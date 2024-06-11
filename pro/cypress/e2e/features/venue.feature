@P0
Feature: Create and update venue

  Scenario: A pro user can add a venue without SIRET
    Given I am logged in
    When I want to add a venue
    And I choose a venue which already has a Siret
    And I add venue without Siret details
    And I validate venue step
    And I skip offer creation
    And I open my venue without Siret resume
    And I add an image to my venue
    Then I should see details of my venue

  Scenario: A pro user can add a venue with SIRET
    Given I am logged in
    When I want to add a venue
    And I add a valid Siret
    And I add venue with Siret details
    And I validate venue step
    And I skip offer creation
    Then I should see my venue with Siret resume

  Scenario: It should update a venue
    Given I am logged in
    When I go to the venue page in Individual section
    And I update Individual section data
    Then Individual section data should be updated
    When I go to the venue page in Paramètres généraux
    And I update Paramètres généraux data
    Then Paramètres généraux data should be updated

  Scenario: It should display venues of selected offerer
    Given I am logged in with the new interface
    When I select offerer "0 - Structure avec justificatif copié"
    Then I should only see these venues
      | Offres numériques | Lieu avec justificatif copié |
