@P0
Feature: Create an individual offer (thing)

  Scenario: It should create an individual offer (thing)
    Given I am logged in
    When I go to "Créer une offre" page
    And I want to create "Un bien physique" offer
    And I fill in details for physical offer
    And I validate offer details step
    And I fill in stocks
    And I validate stocks step
    And I publish my offer
    And I go to offers list
    Then my new physical offer should be displayed
