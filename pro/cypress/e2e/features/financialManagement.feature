@P0
Feature: Download of invoices and reimbursement details

  Background:
    Given I am logged in with the new interface
    And I select offerer "0 - Structure avec justificatif et compte bancaire"
    And I go to the "Gestion financière" page

  Scenario: I can download reimbursement details and invoices
    When I download reimbursement details
    Then I can see the reimbursement details