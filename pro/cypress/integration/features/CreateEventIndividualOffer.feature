@P0
Feature: Create an individual offer (event)

  Scenario: It should create an individual offer
    Given I am logged in
    When I go to "Créer une offre" page
    And I want to create an offer
    And I fill in offer details
    And I fill in prices
    And I fill in recurrence
    And I publish my offer
    And I go to offers list
    Then my new offer should be displayed