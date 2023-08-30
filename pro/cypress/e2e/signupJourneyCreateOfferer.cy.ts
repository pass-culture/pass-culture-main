describe('Signup journey', () => {
  const siret = Math.random().toString().substring(2, 16)

  const welcomeStep = () => {
    // Welcome page
    cy.visit({ method: 'GET', url: '/parcours-inscription' })
    cy.contains('Commencer').click()
  }

  const offererStep = () => {
    // Offerer page
    cy.intercept('GET', `http://localhost:5001/sirene/siret/${siret}`, req =>
      req.reply({
        statusCode: 200,
        body: {
          siret: siret,
          name: 'MINISTERE DE LA CULTURE',
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

    cy.intercept(
      'GET',
      `https://api-adresse.data.gouv.fr/search/?limit=1&q=3 RUE DE VALOIS Paris 75001`,
      req =>
        req.reply({
          statusCode: 200,
          body: {
            type: 'FeatureCollection',
            version: 'draft',
            features: [
              {
                type: 'Feature',
                geometry: { type: 'Point', coordinates: [2.337933, 48.863666] },
                properties: {
                  label: '3 Rue de Valois 75001 Paris',
                  score: 0.8136893939393939,
                  housenumber: '3',
                  id: '75101_9575_00003',
                  name: '3 Rue de Valois',
                  postcode: '75001',
                  citycode: '75101',
                  x: 651428.82,
                  y: 6862829.62,
                  city: 'Paris',
                  district: 'Paris 1er Arrondissement',
                  context: '75, Paris, Île-de-France',
                  type: 'housenumber',
                  importance: 0.61725,
                  street: 'Rue de Valois',
                },
              },
            ],
            attribution: 'BAN',
            licence: 'ETALAB-2.0',
            query: '3 RUE DE VALOIS Paris 75001',
            limit: 1,
          },
        })
    )

    cy.get('#siret').type(siret)
    cy.wait('@getSiret')
    cy.contains('Continuer').click()
    cy.wait('@getSiret')
  }

  const activityStep = () => {
    // Activity page
    cy.get('#venueTypeCode').select('Spectacle vivant')
    cy.get('[name="socialUrls[0]"]').type('https://exemple.com')
    cy.contains('Ajouter un lien').click()
    cy.get('[name="socialUrls[1]"]').type('https://exemple2.com')

    cy.get('[name="targetCustomer.individual"]').check()
    cy.contains('Étape suivante').click()
  }

  const validationStep = () => {
    // Validation page
    cy.contains('Valider et créer ma structure').click()
    cy.url().should('be.equal', 'http://localhost:3001/accueil')
  }

  it('should create offerer', () => {
    cy.login('eac_1_lieu@example.com', 'user@AZERTY123')

    welcomeStep()
    offererStep()

    // Authentication page
    cy.get('#publicName').type('First Offerer')
    cy.contains('Étape suivante').click()

    activityStep()
    validationStep()

    cy.logout()
  })

  it('should ask offerer attachment to a user and create new offerer', () => {
    cy.login('pctest.pro97.0@example.com', 'user@AZERTY123')

    welcomeStep()
    offererStep()

    // Offerer attachment
    cy.contains('Ajouter une nouvelle structure').click()

    // Authentication page
    cy.get('#search-addressAutocomplete').clear()
    cy.get('#search-addressAutocomplete').type('89 Rue la Boétie 75008 Paris')
    cy.get('#list-addressAutocomplete li').first().click()
    cy.contains('Étape suivante').click()

    activityStep()
    validationStep()

    cy.logout()
  })

  it('should attach user to an existing offerer', () => {
    cy.login('pctest.pro93.0@example.com', 'user@AZERTY123')

    welcomeStep()
    offererStep()

    // Offerer attachment
    cy.contains('Rejoindre cet espace').click()

    cy.get('[data-testid="confirm-dialog-button-confirm"]').as(
      'dialogConfirmButton'
    )
    cy.get('@dialogConfirmButton').click()

    cy.contains('Accéder à votre espace').click()

    cy.url().should('be.equal', 'http://localhost:3001/accueil')

    cy.logout()
  })
})
