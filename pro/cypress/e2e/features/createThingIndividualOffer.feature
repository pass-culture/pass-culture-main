@P0
Feature: Create an individual offer (event)

  Scenario: It should create an individual offer
    Given I am logged in
    When I go to "Créer une offre" page
    And I want to create "Un bien physique" offer
    And I fill in details for physical offer
    And I fill in stocks
    And I publish my offer
    And I go to offers list
    Then my new offer should be displayed