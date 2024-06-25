@P0
Feature: Search individual offers

  Background:
    Given I am logged in
    And I go to the "Offres" page

  Scenario: A search with a name should display expected results
    When I select offerer "Cinéma du coin" in offer page
    And I search with the text "Mon offre brouillon avec stock"
    Then These results should be displayed
      |  |  | Titre               | Lieu             | Stocks | Status    |
      |  |  | Mon offre brouillon | Espace des Gnoux |      0 | brouillon |

  Scenario: A search with a EAN should display expected results
    When I select offerer "Réseau de librairies" in offer page
    And I search with the text "9780000000004"
    Then These results should be displayed
      |  |  | Titre            | Lieu         | Stocks | Status     |
      |  |  | Livre 4 avec EAN | Librairie 10 | 10     | publiée    |
      |  |  | Livre 4 avec EAN | Librairie 9  | 10     | désactivée |
      |  |  | Livre 4 avec EAN | Librairie 8  | 10     | publiée    |
      |  |  | Livre 4 avec EAN | Librairie 7  | 10     | publiée    |
      |  |  | Livre 4 avec EAN | Librairie 6  | 10     | en attente |
      |  |  | Livre 4 avec EAN | Librairie 5  | 10     | publiée    |
      |  |  | Livre 4 avec EAN | Librairie 4  | 10     | publiée    |
      |  |  | Livre 4 avec EAN | Librairie 3  | 10     | désactivée |
      |  |  | Livre 4 avec EAN | Librairie 2  | 10     | publiée    |
      |  |  | Livre 4 avec EAN | Librairie 1  | 10     | publiée    |

  # pourrait être un TU/TI, on le met en E2E temporairement
  Scenario: A search with "Mode de création" filter should display expected results
    When I select "Beaux-arts" in "Catégories"
    And I validate my filters
    Then These results should be displayed
      |  |  | Titre      | Lieu                   | Stocks | Status     |
      |  |  | Offer 1617 | La librairie quantique |      0 | désactivée |
      |  |  | Offer 1598 | Club Dorothy           |     20 | publiée    |

  Scenario: A search by offer status should display expected results
    When I select "Validation en attente" in offer status
    Then These results should be displayed
      |  |  | Titre            | Lieu        | Stocks | Status     |
      |  |  | Livre 4 avec EAN | Librairie 6 |     10 | en attente |
      |  |  | Livre 3 avec EAN | Librairie 6 |     10 | en attente |
      |  |  | Livre 2 avec EAN | Librairie 6 |     10 | en attente |
      |  |  | Livre 1 avec EAN | Librairie 6 |     10 | en attente |

  # comme tout est "Manuel" dans la sandbox, automatiser ce test en l'état n'aurait pas beaucoup de sens
  # Scenario: A search by creation mode should display expected results
  #   When I select "Manuel" in "Mode de création"
    
