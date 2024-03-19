import { CONSTANTS } from '../../support/constants'

describe('invalid token', () => {
  it('enter invalid token and verify error message', () => {
    cy.login({
      email: CONSTANTS.emailProAccount,
      password: CONSTANTS.passwordProAccount,
    })
    cy.contains('Guichet').click()

    cy.url().should('include', '/guichet')

    cy.get(CONSTANTS.tokenField).type(CONSTANTS.randomToken)

    cy.contains("La contremarque n'existe pas").should('be.visible')

    cy.contains(CONSTANTS.validateTokenButton).should('be.disabled')

    cy.get(CONSTANTS.tokenField).clear()

    cy.get(CONSTANTS.tokenField).type(CONSTANTS.invalidRandomToken)

    cy.contains(CONSTANTS.validateTokenButton).should('be.disabled')

    cy.contains(
      'La contremarque ne peut pas faire plus de 6 caractères'
    ).should('be.visible')
  })
})
