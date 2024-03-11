import { CONSTANTS } from '../../support/constants'

const connectionLinkExpected = '/connexion'
const inscriptionLinkExpected = '/inscription'

describe('page connexion and inscription', () => {
  it('switch between the two pages connection and inscription using the button signIn and signUp', () => {
    cy.visit(CONSTANTS.connectionLink)

    cy.contains(CONSTANTS.signInButton).should('be.disabled')

    cy.contains(CONSTANTS.signUpButton).click()

    cy.url().should('include', inscriptionLinkExpected)

    cy.contains(CONSTANTS.iAlreadyHaveAnAccountButton).click()

    cy.url().should('include', connectionLinkExpected)
    cy.contains(CONSTANTS.signInButton).should('be.disabled')
  })
})
