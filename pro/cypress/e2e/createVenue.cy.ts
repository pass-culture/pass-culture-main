describe('Create a venue', () => {
  const siret = '222222233' + Math.random().toString().substring(2, 7)
  const venueNameWithSiret = 'Lieu avec Siret ' + siret
  const venueNameWithoutSiret = 'Lieu sans Siret ' + siret // just to distinguish them

  beforeEach(() => {
    cy.intercept('GET', `http://localhost:5001/sirene/siret/${siret}`, (req) =>
      req.reply({
        statusCode: 200,
        body: {
          siret: siret,
          name: 'Ministère de la Culture',
          active: true,
          address: {
            street: '3 RUE DE VALOIS',
            postalCode: '75001',
            city: 'Paris',
          },
          ape_code: '90.03A',
          legal_category_code: '1000',
        },
      })
    ).as('getSiret')

    cy.visit('/connexion')
  })

  it('should create individual venues', () => {
    cy.login({
      email: 'retention_structures@example.com',
      password: 'user@AZERTY123',
    })

    cy.get('#offererId').select('Bar des amis')
    cy.contains('Ajouter un lieu').click()

    // can add a venue without SIRET
    cy.contains('Ce lieu possède un SIRET').click()
    cy.get('#comment').type('Commentaire du lieu sans SIRET')
    cy.get('#name').type(venueNameWithoutSiret)
    cy.get('#search-addressAutocomplete')
      .type('89 Rue la Boétie 75008 Paris')
      .type('{downarrow}{enter}')
    cy.get('#venueType').select('Centre culturel')
    cy.contains('Visuel').click()
    cy.get('#bookingEmail').type('email@axample.com')
    cy.contains('Enregistrer et créer le lieu').click()
    cy.contains('Plus tard').click()
    cy.get(
      'a[aria-label="Gérer la page de ' + venueNameWithoutSiret + '"]'
    ).click()

    // FIX ME: broken for now, remove Accueil click
    // cy.contains('Enregistrer et quitter').click()
    cy.contains('Accueil').click()

    // Create a venue with SIRET
    cy.contains('Ajouter un lieu').click()
    cy.get('#siret').type(siret)
    cy.wait('@getSiret')
    cy.get('#publicName').type(venueNameWithSiret)
    cy.get('#venueType').select('Festival')
    cy.contains('Moteur').click()
    cy.contains('Auditif').click()
    cy.get('#bookingEmail').type('email@axample.com')
    cy.contains('Enregistrer et créer le lieu').click()
    cy.contains('Plus tard').click()
    cy.get(
      'a[aria-label="Gérer la page de ' + venueNameWithSiret + '"]'
    ).click()
    cy.contains('Enregistrer et quitter').click()
    cy.contains('Bienvenue dans l’espace acteurs culturels')
  })
})
