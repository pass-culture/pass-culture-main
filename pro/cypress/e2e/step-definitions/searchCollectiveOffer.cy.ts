import { Given, When } from '@badeball/cypress-cucumber-preprocessor'

Given('I go to Offres collectives view', () => {
  cy.intercept({ method: 'GET', url: '/collective/offers*', times: 1 }).as(
    'collectiveOffers'
  )
  cy.visit('/offres/collectives')
  cy.wait('@collectiveOffers')
})

When('I validate my collective filters', () => {
  cy.intercept({ method: 'GET', url: '/collective/offers*', times: 1 }).as(
    'collectiveOffers'
  )
  cy.findByText('Rechercher').click()
  cy.wait('@collectiveOffers')
})
