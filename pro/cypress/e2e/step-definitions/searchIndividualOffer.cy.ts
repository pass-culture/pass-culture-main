import { When } from '@badeball/cypress-cucumber-preprocessor'

When('I search with the text {string}', (title: string) => {
  cy.findByPlaceholderText('Rechercher par nom d’offre ou par EAN-13').type(
    title
  )
  cy.findByText('Rechercher').click()
})
When('I select {string} in offer status', (filter: string) => {
  cy.findByText('Statut').click()
  cy.findByText(filter).click()
  cy.findByText('Appliquer').click()
})