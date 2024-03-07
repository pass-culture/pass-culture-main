describe('page connexion', () => {
  it('verify connexion page conformity', () => {
    cy.visit('/connexion')

    cy.url().should('include', '/connexion')

    cy.get('#email').should('exist')

    cy.get('#password').should('exist')

    cy.contains('Mot de passe oublié ?')
      .should('have.attr', 'href')
      .and('include', '/demande-mot-de-passe')

    cy.contains('Se connecter').should('be.disabled')

    cy.contains('Créer un compte').should('not.be.disabled')

    cy.contains('Consulter nos recommandations de sécurité')
      .should('have.attr', 'href')
      .and(
        'include',
        'https://aide.passculture.app/hc/fr/articles/4458607720732--Acteurs-Culturels-Comment-assurer-la-s%C3%A9curit%C3%A9-de-votre-compte'
      )

    cy.contains('CGU professionnels')
      .should('have.attr', 'href')
      .and('include', 'https://pass.culture.fr/cgu-professionnels/')

    cy.contains('Charte des Données Personnelles')
      .should('have.attr', 'href')
      .and('include', 'https://pass.culture.fr/donnees-personnelles/')

    cy.contains('Gestion des cookies').should('exist')
  })
})
