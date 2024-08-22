@P0
Feature: Financial Management

  Scenario: Check messages, reimbursement details and offerer selection change
    Given I am logged in with account 2
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

  Scenario: Automatic link venue with bank account
    Given I am logged in
    And I go to the "Gestion financière" page
    And I go to "Informations bancaires" view
    When I remove "Terrain vague" venue from my bank account
    Then no venue should be linked to my account
    When I add "Terrain vague" venue to my bank account
    Then "Terrain vague" venue should be linked to my account