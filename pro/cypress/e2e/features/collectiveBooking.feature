@P0
Feature: Search for collective bookings

  Scenario: It should find collective bookings
    Given I am logged in
    And I go to "Réservations" page
    And I go to "Réservations collectives" page
    And I display offers
    When I search for "Offre" with name "Offer 1640"
    # Then I should see "1" result
    # And I should see my offer