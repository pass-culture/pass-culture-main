describe('Update a venue', () => {
  beforeEach(() => {
    cy.visit('/connexion')
  })

  it('should update a venue', () => {
    cy.login({
      // TODO: when we update the tests data to be standalone,
      // we should have an account with at least 2 permanent venues
      email: 'pctest.admin93.0@example.com',
      password: 'user@AZERTY123',
    })

    // goes to the venue page in Individual section and update data
    cy.findByLabelText('Structure').select('Lieu non dit')
    cy.findByText('Vos pages partenaire').should('be.visible')
    cy.findByText('Carnet d’adresses').should('be.visible')
    cy.findByLabelText('Sélectionnez votre page partenaire *').select(
      'Cinéma de la fin Bis'
    )

    // findByText() et findByRole() marchent pas ici
    cy.contains('Gérer ma page').click()
    cy.findByText('Vos informations pour le grand public').should('be.visible')
    cy.findByText('À propos de votre activité').should('be.visible')
    cy.findByText('Modifier').click()

    cy.findByText('Cinéma de la fin Bis').should('be.visible')
    cy.findAllByLabelText('Description')
      .clear()
      .type('On peut ajouter des choses, vraiment fantastique !!!')
    cy.findByText('Non accessible').click()
    cy.findByText('Psychique ou cognitif').click()
    cy.findByText('Auditif').click()
    cy.intercept({ method: 'PATCH', url: '/venues/*' }).as('patchVenue')
    cy.findByText('Enregistrer et quitter').click()
    cy.wait('@patchVenue')

    cy.findByText('Annuler et quitter').should('not.exist')
    cy.findByText('Vos informations pour le grand public').should('be.visible')
    cy.findByText(
      'On peut ajouter des choses, vraiment fantastique !!!'
    ).should('be.visible')

    // goes to the venue page in "Paramètre de l'activité" and update data
    cy.findByText('Paramètres de l’activité').click()
    cy.findByLabelText(
      'Label du ministère de la Culture ou du Centre national du cinéma et de l’image animée'
    ).select('Musée de France')
    cy.findByLabelText('Informations de retrait')
      .clear()
      .type(
        'En main bien propres, avec un masque et un gel hydroalcoolique, didiou !'
      )
    cy.findByText('Enregistrer et quitter').click()
    cy.findByText('Musée de France').should('be.visible')
  })
})
