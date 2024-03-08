import { CONSTANTS } from '../../support/constants'

describe('page connexion', () => {
  it('verify connexion page conformity', () => {
    cy.visit('/connexion')

    cy.url().should('include', '/connexion')

    cy.get(CONSTANTS.emailId).should('exist')

    cy.get(CONSTANTS.passwordId).should('exist')

    cy.contains('Mot de passe oublié ?')
      .should('have.attr', 'href')
      .and('include', CONSTANTS.request_password_link)

    cy.contains('Se connecter').should('be.disabled')

    cy.contains('Créer un compte').should('not.be.disabled')

    cy.contains('Consulter nos recommandations de sécurité')
      .should('have.attr', 'href')
      .and('include', CONSTANTS.security_recommendations_link)

    cy.contains('CGU professionnels')
      .should('have.attr', 'href')
      .and('include', CONSTANTS.terms_and_conditions_professionals_link)

    cy.contains('Charte des Données Personnelles')
      .should('have.attr', 'href')
      .and('include', CONSTANTS.personal_data_link)

    cy.contains('Gestion des cookies').should('exist')
  })
})
