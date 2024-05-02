@P0
Feature: Adage discovery

  Background:
    Given I go to adage login page with valide token

#   Scenario: it should redirect to adage discovery
#     When I open adage iframe
#     Then the iframe should be display correctly

  Scenario: it should redirect to adage search page with filtered venue
    When I open adage iframe with search page
    Then the iframe search page should be display correctly

  Scenario: it should redirect to a page dedicated to the offer with an active header on the discovery tab
    When I open adage iframe
    And I select first displayed offer
    Then the iframe should be display correctly
