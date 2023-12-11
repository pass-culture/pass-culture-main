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

// TODO Albéric: can be re-added when this issue is solved: https://github.com/testing-library/cypress-testing-library/issues/252
// import '@testing-library/cypress/add-commands'

Cypress.on('uncaught:exception', () => {
  // returning false here prevents Cypress from failing the test
  return false
})

Cypress.Commands.add(
  'login',
  ({ email, password, redirectUrl, acceptCookies = true }) => {
    cy.intercept({ method: 'POST', url: '/users/signin' }).as('signinUser')

    cy.visit(
      redirectUrl
        ? `/connexion?de=${encodeURIComponent(redirectUrl)}`
        : '/connexion'
    )

    if (acceptCookies) {
      cy.acceptCookies()
    }

    cy.get('#email').type(email)
    cy.get('#password').type(password)
    cy.get('button[type=submit]').click()
    cy.wait('@signinUser')

    cy.url().should('contain', redirectUrl ?? '/accueil')
  }
)

Cypress.Commands.add('acceptCookies', () => {
  cy.get('button').contains('Tout accepter').click()
})

export {}
