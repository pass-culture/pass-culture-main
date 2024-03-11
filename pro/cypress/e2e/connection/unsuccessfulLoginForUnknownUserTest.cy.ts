import { CONSTANTS } from '../../support/constants'

const connectionLinkExpected = '/connexion'

describe('page connection', () => {
  it('verify unsuccessful login for unknown user', () => {
    cy.visit(CONSTANTS.connectionLink)

    cy.get(CONSTANTS.emailId).type(CONSTANTS.emailTestData)

    cy.get(CONSTANTS.passwordId).type(CONSTANTS.passwordTestData)

    cy.get('button[type=submit]').click()

    cy.get(CONSTANTS.emailErrorId).should('exist')

    cy.get(CONSTANTS.passwordErrorId).should('exist')

    cy.contains(CONSTANTS.signInButton).should('be.disabled')

    cy.url().should('include', connectionLinkExpected)
  })
})
