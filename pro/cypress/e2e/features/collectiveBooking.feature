@P0
Feature: Search for collective bookings

  Background:
    Given I am logged in
    And I select offerer "eac_2_lieu [BON EAC]"
    And I open the "reservations/collectives" page

  Scenario: It should find collective bookings by offers
    When I display offers
    And I search for "Offre" with text "offer 39"
    Then These 1 results should be displayed
      | Réservation | Nom de l'offre | Établissement                               | Places et prix | Statut  |
      |          80 | offer          | ECOLE ELEMENTAIRE PUBLIQUE FRANCOIS MOISSON | 25 places100 € | annulée |

  Scenario: It should find collective bookings by establishments
    When I display offers
    And I search for "Établissement" with text "LYCEE POLYVALENT METIER ROBERT DOISNEAU"
    Then These 6 results should be displayed
      | Réservation | Nom de l'offre | Établissement                           | Places et prix | Statut      |
      |          79 | offer          | LYCEE POLYVALENT METIER ROBERT DOISNEAU | 25 places100 € | annulée     |
      |          72 | offer          | LYCEE POLYVALENT METIER ROBERT DOISNEAU | 25 places100 € | annulée     |
      |          65 | offer          | LYCEE POLYVALENT METIER ROBERT DOISNEAU | 25 places100 € | remboursée  |
      |          58 | offer          | LYCEE POLYVALENT METIER ROBERT DOISNEAU | 25 places100 € | terminée    |
      |          51 | offer          | LYCEE POLYVALENT METIER ROBERT DOISNEAU | 25 places100 € | confirmée   |
      |          44 | offer          | LYCEE POLYVALENT METIER ROBERT DOISNEAU | 25 places100 € | préréservée |

  Scenario: It should find collective bookings by booking number
    When I display offers
    And I search for "Numéro de réservation" with text "66"
    Then These 1 results should be displayed
      | Réservation | Nom de l'offre | Établissement                               | Places et prix | Statut  |
      |          66 | offer          | ECOLE ELEMENTAIRE PUBLIQUE FRANCOIS MOISSON | 25 places100 € | annulée |
  # @todo: faire un cas de recherche par date (comme dans https://github.com/pass-culture/pass-culture-main/pull/12931) + établissement
  # Scenario: It should find collective bookings with two filters
  #   When I fill venue with "real_venue 1 eac_2_lieu [BON EAC]"
  #   And I display offers
  #   And I search for "Établissement" with text "ECOLE ELEMENTAIRE PUBLIQUE FRANCOIS MOISSON"
  #   Then These results should be displayed
  #     | Réservation | Nom de l'offre | Établissement                               | Places et prix | Statut    |
  #     |          80 | offer        | ECOLE ELEMENTAIRE PUBLIQUE FRANCOIS MOISSON | 25 places100 € | annulée   |
  #     |          66 | offer        | ECOLE ELEMENTAIRE PUBLIQUE FRANCOIS MOISSON | 25 places100 € | annulée   |
  #     |          52 | offer        | ECOLE ELEMENTAIRE PUBLIQUE FRANCOIS MOISSON | 25 places100 € | confirmée |
