import { Given } from '@badeball/cypress-cucumber-preprocessor'

Given('I go to {string} view', (tab: string) => {
  cy.findByText(tab).click()
})

Given('I go to Offres collectives view', () => {
  cy.visit('/offres/collectives')
  cy.wait('@collectiveOffers')
})
