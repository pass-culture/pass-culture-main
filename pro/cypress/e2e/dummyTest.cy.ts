describe('Dummy test', () => {
  it('should load login page', () => {
    cy.visit('/')

    cy.findByText('Bienvenue sur l’espace dédié aux acteurs culturels')
  })
})

export {}
