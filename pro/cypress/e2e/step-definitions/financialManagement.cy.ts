import { Given, Then, When } from '@badeball/cypress-cucumber-preprocessor'

Given('I choose an offerer with financial informations', () => {
  cy.findByLabelText('Structure').select(
    '0 - Structure avec justificatif et compte bancaire'
  )
})

When('I download reimbursement details', () => {
  cy.findByTestId('dropdown-menu-trigger').click()
  cy.findByText(/Télécharger le détail des réservations/).click()
})

Then('I can see the reimbursement details', () => {
  const filename = `${Cypress.config('downloadsFolder')}/remboursements_pass_culture.csv`

  cy.readFile(filename, { timeout: 15000 }).should('not.be.empty')
})
