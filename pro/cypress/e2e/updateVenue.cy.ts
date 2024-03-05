describe('Update a venue', () => {
  beforeEach(() => {
    cy.visit('/connexion')
  })

  it('should update a venue', () => {
    const newName = 'Cinéma de la fin des Bisous'
    cy.login({
      // TODO: when we update the tests data to be standalone,
      // we should have an account with at least 2 permanent venues
      email: 'pctest.admin93.0@example.com',
      password: 'user@AZERTY123',
    })

    cy.get('#offererId').select('Lieu non dit')
    cy.contains('Vos pages partenaire')
    cy.contains('Carnet d’adresses')
    cy.get('#venues').select('Cinéma de la fin Bis')

    cy.contains('Gérer ma page').click()
    cy.contains('À propos de votre activité').should('be.visible')
    cy.contains('Cinéma de la fin Bis').should('be.visible')
    cy.get('#description')
      .clear()
      .type('On peut ajouter des choses, vraiment fantastique !!!')
    cy.contains('Non accessible').click()
    cy.contains('Psychique ou cognitif').click()
    cy.contains('Auditif').click()
    cy.contains('Enregistrer et quitter').click()

    cy.contains('Gérer ma page').click()
    cy.contains('Paramètres de l’activité').click()
    cy.get('#publicName').clear().type(newName)
    cy.get('#venueLabel').select('Musée de France')
    cy.get('#withdrawalDetails')
      .clear()
      .type(
        'En main bien propres, avec un masque et un gel hydroalcoolique, didiou !'
      )
    cy.contains('Enregistrer et quitter').click()
    cy.contains(newName).should('be.visible')
  })
})
