@P0
Feature: Financial Management - messages, links to external help page, reimbursement details

  Background:
    Given I am logged in with the new interface
    And I select offerer "0 - Structure avec justificatif et compte bancaire"
    And I go to the "Gestion financière" page

  Scenario: I can see information message and links to help pages
    Then I can see information message about reimbursement
    And I can see a link to the next reimbursement help page
    When I open the "remboursements" page
    Then I can see a link to the terms and conditions of reimbursement help page

  Scenario: I can download reimbursement details
    When I download reimbursement details
    Then I can see the reimbursement details

  # Scenario: I can download accounting receipt as pdf
  #   Then I can download accounting receipt as pdf
