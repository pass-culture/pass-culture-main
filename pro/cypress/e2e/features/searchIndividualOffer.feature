@P0
Feature: Search individual offers

  Background:
    Given I am logged in
    And I go to the "Offres" page

  Scenario: A search with a name should display expected results
    When I select offerer "Cinéma du coin" in offer page
    And I search with the text "Mon offre brouillon avec stock"
    Then These 1 results should be displayed
      |  |  | Titre               | Lieu             | Stocks | Status    |
      |  |  | Mon offre brouillon | Espace des Gnoux |      0 | brouillon |

  Scenario: A search with a EAN should display expected results
    When I select offerer "Réseau de librairies" in offer page
    And I search with the text "9780000000004"
    Then These 10 results should be displayed
      |  |  | Titre            | Lieu         | Stocks | Status     |
      |  |  | Livre 4 avec EAN | Librairie 10 |     10 | publiée    |
      |  |  | Livre 4 avec EAN | Librairie 9  |     10 | désactivée |
      |  |  | Livre 4 avec EAN | Librairie 8  |     10 | publiée    |
      |  |  | Livre 4 avec EAN | Librairie 7  |     10 | publiée    |
      |  |  | Livre 4 avec EAN | Librairie 6  |     10 | en attente |
      |  |  | Livre 4 avec EAN | Librairie 5  |     10 | publiée    |
      |  |  | Livre 4 avec EAN | Librairie 4  |     10 | publiée    |
      |  |  | Livre 4 avec EAN | Librairie 3  |     10 | désactivée |
      |  |  | Livre 4 avec EAN | Librairie 2  |     10 | publiée    |
      |  |  | Livre 4 avec EAN | Librairie 1  |     10 | publiée    |
  # pourrait être un TU/TI, on le met en E2E temporairement

  Scenario: A search with "Mode de création" filter should display expected results
    When I select "Beaux-arts" in "Catégories"
    And I validate my filters
    Then These 2 results should be displayed
      |  |  | Titre      | Lieu                   | Stocks | Status     |
      |  |  | Offer 1619 | La librairie quantique |      0 | désactivée |
      |  |  | Offer 1600 | Club Dorothy           |     20 | publiée    |

  Scenario: A search by offer status should display expected results
    When I select "Validation en attente" in offer status
    And I validate my filters
    Then These 4 results should be displayed
      |  |  | Titre            | Lieu        | Stocks | Status     |
      |  |  | Livre 4 avec EAN | Librairie 6 |     10 | en attente |
      |  |  | Livre 3 avec EAN | Librairie 6 |     10 | en attente |
      |  |  | Livre 2 avec EAN | Librairie 6 |     10 | en attente |
      |  |  | Livre 1 avec EAN | Librairie 6 |     10 | en attente |

  Scenario: A search by date should display expected results
    When I select a date in one month
    And I validate my filters
    Then These 1 results should be displayed
      |  |  | Titre      | Lieu                                 | Stocks | Status  |
      |  |  | good movie | Herbert Marcuse Entreprise - Salle 1 |  1 000 | expirée |

  Scenario: A search combining several filters should display expected results
    When I search with the text "Offer"
    And I select "Films, vidéos" in "Catégories"
    And I select "Espace des Gnoux" in "Lieu"
    And I select "Publiée" in offer status
    And I validate my filters
    Then These 2 results should be displayed
      |  |  | Titre      | Lieu             | Stocks | Status  |
      |  |  | Offer 1585 | Espace des Gnoux |     40 | publiée |
      |  |  | Offer 1582 | Espace des Gnoux |     60 | publiée |
    When I reset all filters
    Then All filters are empty
    And These 172 results should be displayed
      |  |  | Titre                                | Lieu          | Stocks   | Status     |
      |  |  | H2G2 Le Guide du voyageur galactique | Terrain vague |       42 | publiée    |
      |  |  | Le Diner de Devs                     | Terrain vague | Illimité | publiée    |
      |  |  | Livre 4 avec EAN                     | Librairie 10  |       10 | publiée    |
      |  |  | Livre 3 avec EAN                     | Librairie 10  |       10 | publiée    |
      |  |  | Livre 2 avec EAN                     | Librairie 10  |       10 | publiée    |
      |  |  | Livre 1 avec EAN                     | Librairie 10  |       10 | publiée    |
      |  |  | Livre 4 avec EAN                     | Librairie 9   |       10 | désactivée |
      |  |  | Livre 3 avec EAN                     | Librairie 9   |       10 | désactivée |
      |  |  | Livre 2 avec EAN                     | Librairie 9   |       10 | désactivée |
      |  |  | Livre 1 avec EAN                     | Librairie 9   |       10 | désactivée |
    # 2 premières lignes créés par createThingIndividual et createEventIndividual
  # comme tout est "Manuel" dans la sandbox, automatiser ce test en l'état n'aurait pas beaucoup de sens
  # Scenario: A search by creation mode should display expected results
  #   When I select "Manuel" in "Mode de création"
