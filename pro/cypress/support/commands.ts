/// <reference types="cypress" />
// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
//
// declare global {
//   namespace Cypress {
//     interface Chainable {
//       login(email: string, password: string): Chainable<void>
//       drag(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       dismiss(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       visit(originalFn: CommandOriginalFn, url: string, options: Partial<VisitOptions>): Chainable<Element>
//     }
//   }
// }

import '@testing-library/cypress/add-commands'

Cypress.on('uncaught:exception', () => {
  // returning false here prevents Cypress from failing the test
  return false
})

Cypress.Commands.add('login', ({ email, password, redirectUrl }) => {
  cy.intercept({ method: 'POST', url: '/users/signin' }).as('signinUser')

  cy.visit('/connexion')
  cy.acceptCookies()

  cy.get('#email').type(email)
  cy.get('#password').type(password)
  cy.get('button[type=submit]').click()
  cy.wait('@signinUser')

  cy.url().should('contain', redirectUrl ?? '/accueil')
  cy.findAllByTestId('spinner').should('not.exist')
})

Cypress.Commands.add('acceptCookies', () => {
  cy.get('button', { timeout: 15 * 1000 })
    .contains('Tout accepter')
    .click()
})

Cypress.Commands.add('setFeatureFlags', (features: Feature[]) => {
  cy.request({
    method: 'PATCH',
    url: 'http://localhost:5001/testing/features',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({
      features,
    }),
  })
})

Cypress.Commands.add('getFakeAdageToken', () => {
  cy.request({
    method: 'GET',
    url: 'http://localhost:5001/adage-iframe/testing/token',
  }).then((response) => {
    Cypress.env('adageToken', response.body.token)
  })
})

export {}
