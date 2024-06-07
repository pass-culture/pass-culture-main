@P0
Feature: Search for collective bookings

  Scenario: It should find collective bookings by offers
    Given I am logged in
    And I go to "Réservations" page
    And I go to "Réservations collectives" page
    And I display offers
    When I search for Offre with name "offer 39"
    Then I should see "1" results
    And I should see my Offre  

  Scenario: It should find collective bookings by establishments
    Given I am logged in
    And I go to "Réservations" page
    And I go to "Réservations collectives" page
    And I display offers
    When I search for Établissement with name "LYCEE POLYVALENT METIER ROBERT DOISNEAU"
    Then I should see "1" results
    And I should see my Établissement

  Scenario: It should find collective bookings by booking number
    Given I am logged in
    And I go to "Réservations" page
    And I go to "Réservations collectives" page
    And I display offers
    When I search for Numéro de réservation with number "66"
    Then I should see "1" results
    And I should see my Établissement    

  # pas fini
  Scenario: It should find collective bookings with two filters
    Given I am logged in
    And I go to "Réservations" page
    And I go to "Réservations collectives" page
    And I fill Lieu with ""
    And I display offers
    When I search for Numéro de réservation with number "66"
    Then I should see "1" results
    And I should see my Établissement      