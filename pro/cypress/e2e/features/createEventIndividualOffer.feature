@P0
Feature: Create an individual offer (event)

  # Plante si l'offerer a plusieurs venues
  Scenario: It should create an individual offer (event)
    Given I am logged in
    And I select offerer "Club Dorothy"
    When I go to the "Créer une offre" page
    And I want to create "Un évènement physique daté" offer
    And I fill in offer details
    And I validate event details step
    And I fill in prices
    And I validate prices step
    And I fill in recurrence
    And I validate recurrence step
    And I publish my offer
    And I go to the offers list
    Then my new offer should be displayed
