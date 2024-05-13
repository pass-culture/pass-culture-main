describe('Create a venue', () => {
  // siret of Bar des amis
  let siret: string
  let randomSeed: number
  let venueNameWithSiret: string
  let venueNameWithoutSiret: string

  beforeEach(() => {
    // siret of Bar des amis
    siret = '222222233' + Math.random().toString().substring(2, 7)
    randomSeed = new Date().getTime()
    venueNameWithSiret = 'Lieu avec Siret ' + randomSeed
    venueNameWithoutSiret = 'Lieu sans Siret ' + randomSeed // just to distinguish them

    // mettre l'intercept à part?
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
    cy.intercept({ method: 'GET', url: '/offerers/*' }).as('getOfferer')
    cy.visit('/connexion')
  })

  it('should create individual venues', () => {
    cy.login({
      email: 'retention_structures@example.com',
      password: 'user@AZERTY123',
    })

    cy.findByLabelText('Structure').select('Bar des amis')
    cy.findByText('Ajouter un lieu').click()

    // can add a venue without SIRET
    cy.findByText('Ce lieu possède un SIRET').click()
    cy.findByLabelText('Commentaire du lieu sans SIRET *')
      .type('Commentaire du lieu sans SIRET')
    cy.findByLabelText('Raison sociale *').type(venueNameWithoutSiret)
    cy.findByLabelText('Adresse postale *')
      .type('89 Rue la Boétie 75008 Paris')
      .type('{downarrow}{enter}')
    cy.findByLabelText('Activité principale *').select('Centre culturel')
    cy.findByText('Visuel').click()
    cy.findByLabelText('Adresse email *').type('email@example.com')
    cy.findByText('Enregistrer et créer le lieu').click()
    cy.wait('@getOfferer')
    cy.findByText('Plus tard').click()
    cy.findByRole('link', { name: 'Gérer la page de ' + venueNameWithoutSiret + '' }).click()
    cy.contains(venueNameWithoutSiret).should('be.visible')

    // Create a venue with SIRET
    // TODO: verifier aussi les champs pré-remplis
    cy.findByText('Ajouter un lieu').click()
    cy.findByLabelText('SIRET du lieu *').type(siret)
    cy.wait('@getSiret')
    cy.findByLabelText('Nom public').type(venueNameWithSiret)
    cy.findByLabelText('Activité principale *').select('Festival')
    cy.findByText('Moteur').click()
    cy.findByText('Auditif').click()
    cy.findByLabelText('Adresse email *').type('email@example.com')
    cy.findByText('Enregistrer et créer le lieu').click()
    cy.wait('@getOfferer')
    cy.contains('Plus tard').click()
    cy.findByRole('link', { name: 'Gérer la page de ' + venueNameWithSiret + '' }).click()
    cy.findByText(venueNameWithSiret).should('be.visible')
    cy.findByText('Vos informations pour le grand public').should('be.visible')
  })
})
