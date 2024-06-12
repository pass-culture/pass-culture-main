@P0
Feature: Search collective offers

  Scenario: A search with several filters should display expected results
    Given I am logged in
    And I go to "Offres" page
    And I go to "Offres collectives" view
    When I select "real_venue 1 eac_2_lieu [BON EAC]" in "Lieu"
    And I select "Projection audiovisuelle" in "Format"
    And I validate my filters
    Then These results should be displayed
      |  |  | Titre    | Lieu                              | Établissement           | Status  |
      |  |  | offer 49 | real_venue 1 eac_2_lieu [BON EAC] | Tous les établissements | publiée |
      |  |  | offer 47 | real_venue 1 eac_2_lieu [BON EAC] | Tous les établissements | publiée |
      |  |  | offer 45 | real_venue 1 eac_2_lieu [BON EAC] | Tous les établissements | publiée |
      |  |  | offer 3  | real_venue 1 eac_2_lieu [BON EAC] | Tous les établissements | publiée |
      |  |  | offer 1  | real_venue 1 eac_2_lieu [BON EAC] | Tous les établissements | publiée |
