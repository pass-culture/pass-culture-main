import { CONSTANTS } from '../../support/constants'

describe('signin page', () => {
  it('verify unsuccessful login for unknown user', () => {
    cy.visit(CONSTANTS.signIn)

    cy.get(CONSTANTS.emailId).type(CONSTANTS.randomEmail)

    cy.get(CONSTANTS.passwordId).type(CONSTANTS.randomPassword)

    cy.get('button[type=submit]').click()

    cy.get(CONSTANTS.emailErrorId)
      .should('be.visible')
      .should('have.text', 'Identifiant ou mot de passe incorrect.')

    cy.get(CONSTANTS.passwordErrorId)
      .should('be.visible')
      .should('have.text', 'Identifiant ou mot de passe incorrect.')

    cy.contains(CONSTANTS.signInButton).should('be.disabled')

    cy.url().should('include', CONSTANTS.signIn)
  })
})
