describe('save filters so that you can retrieve them when you return to the search page', () => {
  beforeEach(() => {
    cy.visit('/connexion')
    cy.getFakeAdageToken()
  })

  it('should save filter when page changing', () => {
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe/recherche?token=${adageToken}`)

    cy.findByRole('button', { name: 'Format' }).click()
    cy.findByLabelText('Atelier de pratique').click()
    cy.findAllByRole('button', { name: 'Rechercher' }).eq(1).click()
    cy.findByRole('button', { name: 'Domaine artistique' }).click()
    cy.findByLabelText('Arts numériques').click()
    cy.findAllByRole('button', { name: 'Rechercher' }).eq(1).click()
    cy.findByText('Nous n’avons trouvé aucune offre publiée')

    cy.contains('Mes Favoris').click()
    cy.contains('Rechercher').click()
    cy.findByRole('button', { name: 'Format (1)' }).click()
    cy.findByLabelText('Atelier de pratique').should('be.checked')
    cy.findByRole('button', { name: 'Domaine artistique (1)' }).click()
    cy.findByLabelText('Arts numériques').should('be.checked')
    cy.findByText('Nous n’avons trouvé aucune offre publiée')
  })
})
