import { CONSTANTS } from '../../support/constants'

describe('signup and signin pages', () => {
  it('verify unsuccessful signin for unverified email account', () => {
    cy.visit(CONSTANTS.signUp)

    cy.get(CONSTANTS.lastNameField).type(CONSTANTS.lastName)

    cy.get(CONSTANTS.firstNameField).type(CONSTANTS.firstName)

    cy.get(CONSTANTS.emailField).type(CONSTANTS.randomEmail)

    cy.get(CONSTANTS.passwordField).type(CONSTANTS.randomPassword)

    cy.get(CONSTANTS.phoneNumberField).type(CONSTANTS.phoneNumber)

    // cy.contains('Créer mon compte').click()

    cy.get('button[type=submit]').click()

    cy.url().should('include', CONSTANTS.signUpConfirmationLink)

    cy.visit(CONSTANTS.signIn)

    cy.get(CONSTANTS.emailField).type(CONSTANTS.randomEmail)

    cy.get(CONSTANTS.passwordField).type(CONSTANTS.randomPassword)

    cy.contains('Se connecter').click()

    cy.url().should('include', CONSTANTS.signIn)

    cy.get(CONSTANTS.emailErrorId).should('be.visible')

    cy.get(CONSTANTS.passwordErrorId).should('be.visible')

    cy.contains(CONSTANTS.signInButton).should('be.disabled')
  })
})
