@P0
Feature: Create a venue

  Background:
    Given I am logged in
    And I want to add a venue

  Scenario: A pro user can add a venue without SIRET
    When I choose a venue wich already has a Siret
    And I add venue without Siret details
    And I skip offer creation
    Then I should see my venue without Siret resume

  Scenario: A pro user can add a venue with SIRET
    When I add a valid Siret
    And I add venue with Siret details
    And I skip offer creation
    Then I should see my venue with Siret resume