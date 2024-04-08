describe('Update a venue', () => {
  beforeEach(() => {
    const xhr = new XMLHttpRequest()
    xhr.open('GET', 'http://localhost:5001/e2e/pro/update-venue', false)
    xhr.send() // now your `cy.route` will trigger
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
    cy.contains('Vos pages partenaire').should('be.visible')
    cy.contains('Carnet d’adresses').should('be.visible')
    cy.findByLabelText('Sélectionnez votre page partenaire *').select(
      'Cinéma de la fin Bis'
    )

    cy.contains('Gérer ma page').click()
    cy.contains('Vos informations pour le grand public').should('be.visible')
    cy.contains('À propos de votre activité').should('be.visible')
    cy.contains('Modifier').click()

    cy.contains('Cinéma de la fin Bis').should('be.visible')
    cy.findAllByLabelText('Description')
      .clear()
      .type('On peut ajouter des choses, vraiment fantastique !!!')
    cy.contains('Non accessible').click()
    cy.contains('Psychique ou cognitif').click()
    cy.contains('Auditif').click()
    cy.intercept({ method: 'PATCH', url: '/venues/*' }).as('patchVenue')
    cy.contains('Enregistrer et quitter').click()
    cy.wait('@patchVenue')

    cy.contains('Annuler et quitter').should('not.exist')
    cy.contains('Vos informations pour le grand public').should('be.visible')
    cy.contains('On peut ajouter des choses, vraiment fantastique !!!').should(
      'be.visible'
    )

    // goes to the venue page in "Paramètre de l'activité" and update data
    cy.contains('Paramètres de l’activité').click()
    cy.findByLabelText(
      'Label du ministère de la Culture ou du Centre national du cinéma et de l’image animée'
    ).select('Musée de France')
    cy.findByLabelText('Informations de retrait')
      .clear()
      .type(
        'En main bien propres, avec un masque et un gel hydroalcoolique, didiou !'
      )
    cy.contains('Enregistrer et quitter').click()
    cy.contains('Musée de France').should('be.visible')
  })
})
