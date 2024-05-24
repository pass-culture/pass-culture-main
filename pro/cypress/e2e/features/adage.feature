@P0
Feature: ADAGE discovery

  Background:
    Given I go to adage login page with valid token

  Scenario: It should put an offer in favorite
    When I open adage iframe
    And I add first offer to favorites
    Then the first offer should be added to favorites
    And the first favorite is unselected

  Scenario: It should redirect to adage discovery
    When I open adage iframe
    Then the iframe should be displayed correctly
    And the banner is displayed

  Scenario: It should redirect to a page dedicated to the offer with an active header on the discovery tab
    When I open adage iframe
    And I select first displayed offer
    Then the iframe should be displayed correctly

  Scenario: It should redirect to search page with filtered venue on click in venue card
    When I open adage iframe
    And I select first card venue
    Then the iframe search page should be displayed correctly

  Scenario: It should redirect to search page with filtered domain on click in domain card
    When I open adage iframe
    And I select first card domain
    Then the iframe search page should be displayed correctly
    And the "Architecture" button should be displayed

  Scenario: It should not keep filters after page change
    When I open adage iframe
    And I select first card venue
    Then the iframe search page should be displayed correctly
    When I go back to search page

  Scenario: It should save view type in search page
    When I open adage iframe with search page
    Then offer descriptions are displayed
    When I chose grid view
    Then offer descriptions are not displayed
    When I add first offer to favorites
    And I go to "Mes Favoris" menu
    Then offer descriptions are displayed
    When I go to "Rechercher" menu
    Then offer descriptions are not displayed
    And the first favorite is unselected

  Scenario: It should redirect to adage search page with filtered venue
    When I open adage iframe with venue
    Then the iframe search page should be displayed correctly
    And the "Lieu : Librairie des GTls" button should be displayed

  Scenario: It should save filter when page changing
    When I open adage iframe with venue
    And I select "Atelier de pratique" in "Format" filter
    And I select "Arts numériques" in "Domaine artistique" filter
    Then I see no offer
    When I go to "Mes Favoris" menu
    And I go to "Rechercher" menu
    And "Atelier de pratique" in "Format (1)" filter is selected
    And "Arts numériques" in "Domaine artistique (1)" filter is selected
    Then I see no offer
