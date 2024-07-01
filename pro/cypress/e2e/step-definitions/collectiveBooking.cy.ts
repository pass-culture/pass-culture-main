import { When } from '@badeball/cypress-cucumber-preprocessor'

When('I display offers', () => {
  cy.findByText('Afficher').click()
  cy.findByTestId('spinner').should('not.exist')
})

When(
  'I search for {string} with text {string}',
  (criteria: string, search: string) => {
    cy.findByTestId('select-omnisearch-criteria').select(criteria)
    cy.findByTestId('omnisearch-filter-input-text').type(search)
  }
)

When('I fill venue with {string}', (venue: string) => {
  cy.findByLabelText('Lieu').select(venue)
})
