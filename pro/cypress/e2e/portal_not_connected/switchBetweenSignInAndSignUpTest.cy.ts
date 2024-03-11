import { CONSTANTS } from '../../support/constants'

describe('page signin and signup', () => {
  it('switch between the two pages singin and singup the two buttons', () => {
    cy.visit(CONSTANTS.signIn)

    cy.contains(CONSTANTS.signInButton).should('be.disabled')

    cy.contains(CONSTANTS.signUpButton).click()

    cy.url().should('include', CONSTANTS.signUp)

    cy.contains(CONSTANTS.iAlreadyHaveAnAccountButton).click()

    cy.url().should('include', CONSTANTS.signIn)
    cy.contains(CONSTANTS.signInButton).should('be.disabled')
  })
})
