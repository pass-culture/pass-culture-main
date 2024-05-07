@P0
Feature: Adage discovery

  Background:
    Given I go to adage login page with valide token

#   Scenario: it should redirect to adage discovery
#     When I open adage iframe
#     Then the iframe should be display correctly
#     And the banner is displayed

#   Scenario: it should redirect to adage search page with filtered venue
#     When I open adage iframe with search page
#     Then the iframe search page should be display correctly
#     And the "Lieu : Librairie des GTls" button should be displayed

#   Scenario: it should redirect to a page dedicated to the offer with an active header on the discovery tab
#     When I open adage iframe
#     And I select first displayed offer
#     Then the iframe should be display correctly

#   Scenario: it should redirect to search page with filtered venue on click in venue card
#     When I open adage iframe
#     And I select first card venue
#     Then the iframe search page should be display correctly

#   Scenario: it should redirect to search page with filtered domain on click in domain card
#     When I open adage iframe
#     And I select first card domain
#     Then the iframe search page should be display correctly
#     And the "Architecture" button should be displayed

#   Scenario: it should not keep filters after page change
#     When I open adage iframe
#     And I select first card venue
#     Then the iframe search page should be display correctly
#     When I go back to search page    

#   Scenario: should put an offer in favorite
#     When I open adage iframe
#     And I add first offer to favorites
#     Then the first offer should be added to favorites

  Scenario: it should save filter when page changing
    When I open adage iframe with search page
    And I select "Atelier de pratique" in "Format" filter
    And I select "Arts numériques" in "Domaine artistique" filter
    Then I see no offer
    When I go to "Mes Favoris" menu
    Then stuff happens    