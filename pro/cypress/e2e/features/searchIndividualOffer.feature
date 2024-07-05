@P0
Feature: Search individual offers

  Background:
    Given pro user new nav has been created
    And individual offers has been created
    And I am logged in
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

  Scenario: A search with "Catégories" filter should display expected results
    When I select "Jeux" in "Catégories"
    And I validate my filters
    Then These 1 results should be displayed
      |  |  | Titre | Lieu          | Stocks | Status  |
      |  |  | Offer | Terrain vague |     16 | expirée |

  Scenario: A search by offer status should display expected results
    And I select "Publiée" in offer status
    And I validate my filters
    Then These 5 results should be displayed
      |  |  | Titre | Lieu                           | Stocks | Status  |
      |  |  | Offer | Terrain vague                  |     20 | publiée |
      |  |  | Offer | Bar des amis - Offre numérique |     20 | publiée |
      |  |  | Offer | Terrain vague                  |     40 | publiée |
      |  |  | Offer | Terrain vague                  |     40 | publiée |
      |  |  | Offer | Terrain vague                  |     40 | publiée |

  Scenario: A search by date should display expected results
    When I select offerer "Michel Léon" in offer page
    And I select a date in one month
    And I validate my filters
    Then These 1 results should be displayed
      |  |  | Titre                            | Lieu                    | Stocks | Status  |
      |  |  | Un concert d'electro inoubliable | Michel et son accordéon |  1 000 | publiée |

  Scenario: A search combining several filters should display expected results
    When I search with the text "Offer"
    And I select "Films, vidéos" in "Catégories"
    And I select "Terrain vague" in "Lieu"
    And I select "Publiée" in offer status
    And I validate my filters
    Then These 3 results should be displayed
      |  |  | Titre | Lieu          | Stocks | Status  |
      |  |  | Offer | Terrain vague |     40 | publiée |
      |  |  | Offer | Terrain vague |     40 | publiée |
      |  |  | Offer | Terrain vague |     40 | publiée |
    When I reset all filters
    Then All filters are empty
    And These 12 results should be displayed
      |  |  | Titre                          | Lieu                           | Stocks | Status     |
      |  |  | Mon offre brouillon avec stock | Terrain vague                  |  1 000 | brouillon  |
      |  |  | Mon offre brouillon            | Terrain vague                  |      0 | brouillon  |
      |  |  | Offer                          | Terrain vague                  |     16 | expirée    |
      |  |  | Offer                          | Terrain vague                  |     20 | publiée    |
      |  |  | Offer                          | Terrain vague                  |      0 | désactivée |
      |  |  | Offer                          | Bar des amis - Offre numérique |     20 | publiée    |
      |  |  | Offer                          | Terrain vague                  |     16 | expirée    |
      |  |  | Offer                          | Terrain vague                  |     40 | publiée    |
      |  |  | Offer                          | Terrain vague                  |     40 | publiée    |
      |  |  | Offer                          | Terrain vague                  |      0 | désactivée |
  # comme tout est "Manuel" dans la sandbox, automatiser ce test en l'état n'aurait pas beaucoup de sens
  # Scenario: A search by creation mode should display expected results
  #   When I select "Manuel" in "Mode de création"
