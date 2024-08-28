@P0
Feature: Modify a digital individual offer

  Scenario: I should be able to modify the url of a digital offer
    Given I activate a feature flag "WIP_SPLIT_OFFER"
    And I am logged in with account 2
    When I go to the "Offres" page
    And I open the first offer in the list
    And I display Informations pratiques tab
    And I edit the offer displayed
    And I update the url link
    And I open the first offer in the list
    And I display Informations pratiques tab
    Then the url updated is retrieved in the details of the offer
