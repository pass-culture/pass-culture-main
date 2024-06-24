@P0
Feature: Financial Management - messages, links to external help page, reimbursement details

  Scenario: Check messages, reimbursement details and offerer selection change
    Given I am logged in with the new interface
    When I go to the "Gestion financière" page
    Then I can see information message about reimbursement
    And I can see a link to the next reimbursement help page
    And I can see a link to the terms and conditions of reimbursement help page
    When I select offerer "1 - [CB] Structure avec des coordonnées bancaires dans différents états"
    Then No receipt results should be displayed
    When I select offerer "0 - Structure avec justificatif et compte bancaire"
    Then These receipt results should be displayed
      | Date du justificatif | Type de document | Compte bancaire | N° de virement                        | Montant remboursé | Actions |
      |                      |                  | Remboursement   | Libellé des coordonnées bancaires n°0 | VIR1              |         |
    When I download reimbursement details
    Then I can see the reimbursement details
  # Scenario: I can download accounting receipt as pdf
  #   Then I can download accounting receipt as pdf
