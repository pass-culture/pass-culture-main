import { CONSTANTS } from '../../support/constants'

const connexionLinkExpected = '/connexion'
const inscriptionLinkExpected = '/inscription'

describe('page connexion and inscription', () => {
  it('switch between the two pages connexion and inscription using the button signIn and signUp', () => {
    cy.visit(CONSTANTS.connexionLink)

    cy.contains(CONSTANTS.signInButton).should('be.disabled')

    cy.contains(CONSTANTS.signUpButton).click()

    cy.url().should('include', inscriptionLinkExpected)

    cy.contains(CONSTANTS.iAlreadyHaveAnAccountButton).click()

    cy.url().should('include', connexionLinkExpected)
    cy.contains(CONSTANTS.signInButton).should('be.disabled')
  })
})
