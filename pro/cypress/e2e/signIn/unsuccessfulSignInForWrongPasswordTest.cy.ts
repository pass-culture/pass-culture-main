import { CONSTANTS } from '../../support/constants'

describe('signin page', () => {
  it('verify unsuccessful signin for wrong password', () => {
    cy.visit(CONSTANTS.signIn)

    cy.get(CONSTANTS.emailId).type(CONSTANTS.emailProAccount)

    cy.get(CONSTANTS.passwordId).type(CONSTANTS.passwordTestData)

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
