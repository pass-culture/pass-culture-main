import { Given, When } from '@badeball/cypress-cucumber-preprocessor'

Given('I go to {string} view', (tab: string) => {
  cy.findByText(tab).click()
})

Given('I go to Offres collectives view', () => {
  cy.intercept({ method: 'GET', url: '/collective/offers*' }).as(
    'collectiveOffers'
  )
  cy.visit('/offres/collectives')
  cy.wait('@collectiveOffers')
})


