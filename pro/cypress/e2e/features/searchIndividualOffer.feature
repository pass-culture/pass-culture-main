@P0
Feature: Search individual offers

  Background:
    Given I am logged in with account 1
    And I go to the "Offres" page

  Scenario: A search with a name should display expected results
    When I select offerer "Cinéma du coin" in offer page
    And I search with the text "Mon offre brouillon avec stock"
    And I validate my filters
    Then These 1 results should be displayed
      |  |  | Titre               | Lieu             | Stocks | Status    |
      |  |  | Mon offre brouillon | Espace des Gnoux |      0 | brouillon |

  Scenario: A search with a EAN should display expected results
    When I select offerer "Réseau de librairies" in offer page
    And I search with the text "9780000000004"
    And I validate my filters
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

  Scenario: A search with "Catégories" filter should display expected results
    When I select "Jeux" in "Catégories"
    And I validate my filters
    Then These 1 results should be displayed
      |  |  | Titre | Lieu          | Stocks | Status  |
      |  |  | Offer | Terrain vague |     16 | expirée |

  Scenario: A search by offer status should display expected results
    When I select offerer "Réseau de librairies" in offer page
    And I select "Publiée" in offer status
    And I validate my filters
    Then These 28 results should be displayed
      |  |  | Titre            | Lieu         | Stocks | Status  |
      |  |  | Livre 4 avec EAN | Librairie 10 |     10 | publiée |
      |  |  | Livre 3 avec EAN | Librairie 10 |     10 | publiée |
      |  |  | Livre 2 avec EAN | Librairie 10 |     10 | publiée |
      |  |  | Livre 1 avec EAN | Librairie 10 |     10 | publiée |
      |  |  | Livre 4 avec EAN | Librairie 8  |     10 | publiée |
      |  |  | Livre 3 avec EAN | Librairie 8  |     10 | publiée |
      |  |  | Livre 2 avec EAN | Librairie 8  |     10 | publiée |
      |  |  | Livre 1 avec EAN | Librairie 8  |     10 | publiée |
      |  |  | Livre 4 avec EAN | Librairie 7  |     10 | publiée |
      |  |  | Livre 3 avec EAN | Librairie 7  |     10 | publiée |

  Scenario: A search by date should display expected results
    When I select offerer "Michel Léon" in offer page
    And I select a date in one month
    And I validate my filters
    Then These 1 results should be displayed
      |  |  | Titre                            | Lieu                    | Stocks | Status  |
      |  |  | Un concert d'electro inoubliable | Michel et son accordéon |  1 000 | publiée |

  Scenario: A search combining several filters should display expected results
    When I select offerer "Réseau de librairies" in offer page
    And I search with the text "Livre"
    And I validate my filters
    And I select "Livre" in "Catégories"
    And I select "Librairie 10" in "Lieu"
    And I select "Publiée" in offer status
    And I validate my filters
    Then These 4 results should be displayed
      |  |  | Titre            | Lieu         | Stocks | Status  |
      |  |  | Livre 4 avec EAN | Librairie 10 |     10 | publiée |
      |  |  | Livre 3 avec EAN | Librairie 10 |     10 | publiée |
      |  |  | Livre 2 avec EAN | Librairie 10 |     10 | publiée |
      |  |  | Livre 1 avec EAN | Librairie 10 |     10 | publiée |
    When I reset all filters
    Then All filters are empty
    And These 40 results should be displayed
      |  |  | Titre            | Lieu         | Stocks | Status     |
      |  |  | Livre 4 avec EAN | Librairie 10 |     10 | publiée    |
      |  |  | Livre 3 avec EAN | Librairie 10 |     10 | publiée    |
      |  |  | Livre 2 avec EAN | Librairie 10 |     10 | publiée    |
      |  |  | Livre 1 avec EAN | Librairie 10 |     10 | publiée    |
      |  |  | Livre 4 avec EAN | Librairie 9  |     10 | désactivée |
      |  |  | Livre 3 avec EAN | Librairie 9  |     10 | désactivée |
      |  |  | Livre 2 avec EAN | Librairie 9  |     10 | désactivée |
      |  |  | Livre 1 avec EAN | Librairie 9  |     10 | désactivée |
      |  |  | Livre 4 avec EAN | Librairie 8  |     10 | publiée    |
      |  |  | Livre 3 avec EAN | Librairie 8  |     10 | publiée    |
  # comme tout est "Manuel" dans la sandbox, automatiser ce test en l'état n'aurait pas beaucoup de sens
  # Scenario: A search by creation mode should display expected results
  #   When I select "Manuel" in "Mode de création"
