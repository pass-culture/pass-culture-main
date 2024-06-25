import { When } from '@badeball/cypress-cucumber-preprocessor'

When('I search with the text {string}', (title: string) => {
  cy.findByPlaceholderText('Rechercher par nom d’offre ou par EAN-13').type(
    title
  )
  cy.findByText('Rechercher').click()
})

When('I select offerer {string} in offer page', (offererName: string) => {
  cy.intercept({ method: 'GET', url: '/venues?offererId=*' }).as('getOffererId')
  cy.findByTestId('offerer-select').click()
  cy.findByText(/Changer de structure/).click()
  cy.findByTestId('offerers-selection-menu').findByText(offererName).click()
  cy.wait('@getOffererId')
  cy.findAllByTestId('spinner').should('not.exist')
})
When('I select {string} in offer status', (filter: string) => {
  cy.findByText('Statut').click()
  cy.findByText(filter).click()
  cy.findByText('Appliquer').click()
})
