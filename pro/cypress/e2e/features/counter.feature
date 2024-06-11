@P0
Feature: Counter (Guichet) feature

  Background:
    Given I am logged in with new interface
    And I go to "Guichet" page

  Scenario: It should display identity check message
    Then Identity check message is displayed
    And I can click and open "Modalités de retrait et CGU" page

#   Scenario: Saisie et validation d'une nouvelle contremarque @todo: besoin de données
#     When I add this countermark "2XTM3W"
#     And I validate the countermark // @todo: contremarque regénérées à chaque lancement de sandbox
#     Then The booking is done

  Scenario: It should decline a non-valid countermark
    When I add this countermark "XXXXXX"
    Then The countermark is refused because invalid

#   Scenario: Saisie et invalidation d'une contremarque déjà validée @todo: besoin de données
#     When I add this countermark "2XTM3W"
#     And I validate the countermark
#     Then...

#   Scenario: Saisie d'une contremarque d'un autre pro @todo: besoin de données
#     When I add this countermark "2XTM3W"
#     And I validate the countermark
#     Then...

#   Scenario: Saisie de la contremarque d'une réservation non confirmée @todo: besoin de données
#     When I add this countermark "2XTM3W"
#     And I validate the countermark
#     Then...

#   Scenario: Saisie de la contremarque d'une réservation annulée @todo: besoin de données
#     When I add this countermark "2XTM3W"
#     And I validate the countermark
#     Then...

#   Scenario: Saisie de la contremarque d'une réservation déjà remboursée @todo: besoin de données
#     When I add this countermark "2XTM3W"
#     And I validate the countermark
#     Then...