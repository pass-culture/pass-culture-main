describe('Update a venue', () => {
  beforeEach(() => {
    cy.visit('/connexion')
    cy.setFeatureFlags([{ name: 'WIP_PARTNER_PAGE', isActive: true }])
  })

  afterEach(() => {
    cy.setFeatureFlags([{ name: 'WIP_PARTNER_PAGE', isActive: false }])
  })

  it('should update a venue', () => {
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
    cy.contains('Informations du lieu')
    cy.contains('Cinéma de la fin Bis')
  })
})
