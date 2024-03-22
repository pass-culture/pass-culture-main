import { CONSTANTS } from '../../support/constants'

describe('signin page', () => {
  it('verify unsuccessful signin for wrong password', () => {
    cy.visit(CONSTANTS.signIn)

    cy.get(CONSTANTS.emailField).type(CONSTANTS.emailProAccount)

    cy.get(CONSTANTS.passwordField).type(CONSTANTS.randomPassword)

    cy.get('button[type=submit]').click()

    cy.get(CONSTANTS.emailErrorId)
      .should('be.visible')
      .should('have.text', CONSTANTS.incorrectUsernameOrPasswordText)

    cy.get(CONSTANTS.passwordErrorId)
      .should('be.visible')
      .should('have.text', CONSTANTS.incorrectUsernameOrPasswordText)

    cy.contains(CONSTANTS.signInButton).should('be.disabled')

    cy.url().should('include', CONSTANTS.signIn)
  })
})
