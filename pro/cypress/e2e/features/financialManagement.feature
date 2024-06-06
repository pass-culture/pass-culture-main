@P0
Feature: Download of invoices and reimbursement details

  Background:
    Given I am logged in with financial informations
    And I choose an offerer with financial informations
    And I go to "Gestion financière" page

  Scenario: I can download reimbursement details and invoices
    When I download reimbursement details
    Then I can see the reimbursement details