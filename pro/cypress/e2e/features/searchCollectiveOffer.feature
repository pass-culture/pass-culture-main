@P0
Feature: Search collective offers

  Scenario: A search with several filters should display expected results
    Given I am logged in
    And I select offerer "eac_2_lieu [BON EAC]"
    When I go to Offres collectives view
    And I select "real_venue 1 eac_2_lieu [BON EAC]" in "Lieu"
    And I select "Projection audiovisuelle" in "Format"
    And I validate my filters
    Then These 5 results should be displayed
      |  |  | Titre | Lieu                              | Établissement           | Status  |
      |  |  | offer | real_venue 1 eac_2_lieu [BON EAC] | Tous les établissements | publiée |
      |  |  | offer | real_venue 1 eac_2_lieu [BON EAC] | Tous les établissements | publiée |
      |  |  | offer | real_venue 1 eac_2_lieu [BON EAC] | Tous les établissements | publiée |
      |  |  | offer | real_venue 1 eac_2_lieu [BON EAC] | Tous les établissements | publiée |
      |  |  | offer | real_venue 1 eac_2_lieu [BON EAC] | Tous les établissements | publiée |
