describe('Dummy test', () => {
  it('should load login page', () => {
    cy.visit('/')

    cy.contains('Bienvenue sur l’espace dédié aux acteurs culturels')
  })
})

export {}
