import { When, Given } from '@badeball/cypress-cucumber-preprocessor'

Given('I open {string} page', (page: string) => {
  cy.visit('/' + page)
})

When('I go to {string} page', (page: string) => {
  cy.findAllByText(page).first().click()
})

Given('I am logged in', () => {
  cy.login({
    email: 'retention_structures@example.com',
    password: 'user@AZERTY123',
  })
})

Given('I am logged in with financial informations', () => {
  cy.login({
    email: 'activation_new_nav@example.com',
    password: 'user@AZERTY123',
  })
})

// créer un seul scénario createOffers avec son step-def
When('I want to create {string} offer', (offerType: string) => {
  cy.findByText('Au grand public').click()
  cy.findByText(offerType).click()

  cy.intercept({ method: 'GET', url: '/offers/categories' }).as('getCategories')
  cy.findByText('Étape suivante').click()
  cy.wait('@getCategories')
})
