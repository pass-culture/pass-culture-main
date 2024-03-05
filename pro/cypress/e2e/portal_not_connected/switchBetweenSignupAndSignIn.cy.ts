describe('Test switch between Signup and signin', () => {
  it('visit connexion page and switch between the two pages', () => {
  cy.visit('/connexion')
  // verify button "Se connecter" is disabled
  cy.contains('Se connecter').should('be.disabled')
  // click on button "Creer un compte"
  cy.contains('Créer un compte').click()
  cy.intercept('/inscription').as('requests')
  cy.get('@requests.all')
  cy.url().should('include', '/inscription')
  // click on button "J’ai déjà un compte"
  cy.contains('J’ai déjà un compte').click()
  cy.intercept('/connexion').as('requests')
  cy.get('@requests.all')
  cy.url().should('include', '/connexion')
  // verify button "Se connecter" is disabled
  cy.contains('Se connecter').should('be.disabled')
  })
})

