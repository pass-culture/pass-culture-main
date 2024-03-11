import { CONSTANTS } from '../../support/constants'

const connectionLinkExpected = '/connexion'

describe('page connection', () => {
  it('verify connection page conformity', () => {
    cy.visit(CONSTANTS.connectionLink)

    cy.url().should('include', connectionLinkExpected)

    cy.get(CONSTANTS.emailId).should('exist')

    cy.get(CONSTANTS.passwordId).should('exist')

    cy.contains(CONSTANTS.forgotPasswordText)
      .should('have.attr', 'href')
      .and('include', CONSTANTS.requestPasswordLink)

    cy.contains(CONSTANTS.signInButton).should('be.disabled')

    cy.contains(CONSTANTS.signUpButton).should('not.be.disabled')

    cy.contains(CONSTANTS.securityRecommendationsText)
      .should('have.attr', 'href')
      .and('include', CONSTANTS.securityRecommendationsLink)

    cy.contains(CONSTANTS.termsAndConditionsProfessionalsText)
      .should('have.attr', 'href')
      .and('include', CONSTANTS.termsAndConditionsProfessionalsLink)

    cy.contains(CONSTANTS.personalDataText)
      .should('have.attr', 'href')
      .and('include', CONSTANTS.personalDataLink)

    cy.contains(CONSTANTS.cookieManagementWindow).should('exist')
  })
})
