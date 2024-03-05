describe('Test switch between signup and signin', () => {
  it('visit connexion page and switch between the two pages', () => {
    cy.visit('/connexion')

    cy.contains('Se connecter').should('be.disabled')

    cy.contains('Créer un compte').click()

    cy.url().should('include', '/inscription')

    cy.contains('J’ai déjà un compte').click()

    cy.url().should('include', '/connexion')
    cy.contains('Se connecter').should('be.disabled')
  })
})
