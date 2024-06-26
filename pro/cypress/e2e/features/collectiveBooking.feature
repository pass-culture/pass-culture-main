@P0
Feature: Search for collective bookings

  Background:
    Given I am logged in
    And I select offerer "eac_2_lieu [BON EAC]"
    And I open the "reservations/collectives" page

  Scenario: It should find collective bookings by offers
    When I display offers
    And I search for "Offre" with text "offer 39"
    Then These results should be displayed
      | Réservation | Nom de l'offre | Établissement                               | Places et prix | Statut  |
      |          80 | offer 39       | ECOLE ELEMENTAIRE PUBLIQUE FRANCOIS MOISSON | 25 places100 € | annulée |

  Scenario: It should find collective bookings by establishments
    When I display offers
    And I search for "Établissement" with text "LYCEE POLYVALENT METIER ROBERT DOISNEAU"
    Then These results should be displayed
      | Réservation | Nom de l'offre | Établissement                           | Places et prix | Statut      |
      |          79 | offer 38       | LYCEE POLYVALENT METIER ROBERT DOISNEAU | 25 places100 € | annulée     |
      |          72 | offer 31       | LYCEE POLYVALENT METIER ROBERT DOISNEAU | 25 places100 € | annulée     |
      |          65 | offer 24       | LYCEE POLYVALENT METIER ROBERT DOISNEAU | 25 places100 € | remboursée  |

  Scenario: It should find collective bookings by booking number
    When I display offers
    And I search for "Numéro de réservation" with text "66"
    Then These results should be displayed
      | Réservation | Nom de l'offre | Établissement                               | Places et prix | Statut  |
      |          66 | offer 25       | ECOLE ELEMENTAIRE PUBLIQUE FRANCOIS MOISSON | 25 places100 € | annulée |

