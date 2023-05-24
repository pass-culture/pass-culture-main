describe('Dummy test', () => {
  it('should login', () => {
    cy.login('pctest.admin93.0@example.com', 'user@AZERTY123')
      .url()
      .should('be.equal', 'http://localhost:3001/accueil')
  })

    cy.contains('Bienvenue dans l’espace acteurs culturels')
  })
})

export {}
