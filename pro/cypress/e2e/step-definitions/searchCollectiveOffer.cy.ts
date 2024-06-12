import { Given, When } from '@badeball/cypress-cucumber-preprocessor'

Given('I go to {string} view', (tab: string) => {
  cy.findByText(tab).click()
})

When('I search for {string} in {string}', (option: string, filter: string) => {
  cy.findByLabelText(filter).select(option)
})

When('I validate my filters', () => {
  cy.findByText('Rechercher').click()
})
