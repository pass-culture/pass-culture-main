import { CONSTANTS } from '../../support/constants'

describe('signup and signin pages', () => {
  it('verify unsuccessful signin for unverified email account', () => {
    cy.visit(CONSTANTS.signUp)

    cy.get(CONSTANTS.lastNameId).type(CONSTANTS.randomLastName)

    cy.get(CONSTANTS.firstNameId).type(CONSTANTS.randomFirstName)

    cy.get(CONSTANTS.emailId).type(CONSTANTS.randomEmail)

    cy.get(CONSTANTS.passwordId).type(CONSTANTS.randomPassword)

    cy.get(CONSTANTS.phoneNumberId).type(CONSTANTS.randomPhoneNumber)

    cy.intercept({ method: CONSTANTS.post, url: CONSTANTS.signUpApi }).as(
      'signupUser'
    )
    cy.get('button[type=submit]').click()

    cy.wait('@signupUser')

    cy.url().should('include', CONSTANTS.signUpConfirmationLink)

    cy.visit(CONSTANTS.signIn)

    cy.get(CONSTANTS.emailId).type(CONSTANTS.randomEmail)

    cy.get(CONSTANTS.passwordId).type(CONSTANTS.randomPassword)

    cy.get('button[type=submit]').click()

    cy.url().should('include', CONSTANTS.signIn)

    cy.get(CONSTANTS.emailErrorId)
      .should('be.visible')
      .should('have.text', 'Identifiant ou mot de passe incorrect.')

    cy.get(CONSTANTS.passwordErrorId)
      .should('be.visible')
      .should('have.text', 'Identifiant ou mot de passe incorrect.')

    cy.contains(CONSTANTS.signInButton).should('be.disabled')
  })
})
