import { When, Then, DataTable } from '@badeball/cypress-cucumber-preprocessor'

When('I search with the text {string}', (title: string) => {
  cy.findByPlaceholderText('Rechercher par nom d’offre ou par EAN-13').type(
    title
  )
  cy.findByText('Rechercher').click()
})
