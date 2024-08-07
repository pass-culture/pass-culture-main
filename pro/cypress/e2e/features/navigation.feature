@P0
Feature: User navigation

  Scenario: I should see the top of the page when changing page
    Given I am logged in
    And I select offerer "Cinéma du coin"
    When I scroll to my venue
    And I want to update that venue
    Then I should be at the top of the page

