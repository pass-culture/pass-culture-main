// TODO test is flaky, investigate flakkyness
describe.skip('Signup journey', () => {
  const siret = Math.random().toString().substring(2, 16)
  const offererName = 'MINISTERE DE LA CULTURE'

  beforeEach(() => {
    cy.intercept('GET', `http://localhost:5001/sirene/siret/${siret}`, (req) =>
      req.reply({
        statusCode: 200,
        body: {
          siret: siret,
          name: offererName,
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
      (req) =>
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
  })

  // TODO: bon candidat à des scénarios gherkin !

  // it('should create offerer', () => {
  //   cy.login({
  //     email: 'eac_1_lieu@example.com',
  //     password: 'user@AZERTY123',
  //     redirectUrl: '/parcours-inscription',
  //   })

  //   // Welcome page
  //   cy.findByText('Commencer').click()

  //   // Offerer page
  //   cy.findByLabelText('Numéro de SIRET à 14 chiffres *').type(siret)
  //   cy.wait('@getSiret')
  //   cy.findByText('Continuer').click()
  //   cy.wait('@getSiret')

  //   // Authentication page
  //   cy.findByLabelText('Nom public').type('First Offerer')
  //   cy.findByText('Étape suivante').click()

  //   // Activity page
  //   cy.findByLabelText('Activité principale *').select('Spectacle vivant')
  //   cy.findByLabelText('Site internet, réseau social').type(
  //     'https://exemple.com'
  //   )
  //   cy.findByText('Ajouter un lien').click()
  //   // manque un data-testid ou un placeholder
  //   cy.get('[name="socialUrls[1]"]').type('https://exemple2.com')

  //   cy.findByText('Au grand public').click()
  //   cy.findByText('Étape suivante').click()

  //   // Validation page
  //   cy.intercept({ method: 'POST', url: '/offerers/new' }).as('createOfferer')
  //   cy.findByText('Valider et créer ma structure').click()
  //   cy.wait('@createOfferer').its('response.statusCode').should('eq', 201)

  //   // Homepage
  //   cy.url().should('contain', '/accueil')
  // })

  // it('should ask offerer attachment to a user and create new offerer', () => {
  //   cy.login({
  //     email: 'retention@example.com',
  //     password: 'user@AZERTY123',
  //     redirectUrl: '/parcours-inscription',
  //   })

  //   // Welcome page
  //   cy.findByText('Commencer').click()

  //   // Offerer page
  //   cy.findByLabelText('Numéro de SIRET à 14 chiffres *').type(siret)
  //   cy.wait('@getSiret')
  //   cy.findByText('Continuer').click()
  //   cy.wait('@getSiret')

  //   // Offerer attachment
  //   cy.findByText('Ajouter une nouvelle structure').click()

  //   // Authentication page
  //   cy.findByLabelText('Adresse postale *')
  //     .clear()
  //     .type('89 Rue la Boétie 75008 Paris')
  //   cy.findByRole('option', { name: '89 Rue la Boétie 75008 Paris' }).click()

  //   cy.findByText('Étape suivante').click()

  //   // Activity page
  //   cy.findByLabelText('Activité principale *').select('Spectacle vivant')

  //   cy.findByText('Au grand public').click()
  //   cy.findByText('Étape suivante').click()

  //   // Validation page
  //   // TODO: ajouter des assertions
  //   cy.intercept({ method: 'POST', url: '/offerers/new' }).as('createOfferer')
  //   cy.findByText('Valider et créer ma structure').click()
  //   cy.wait('@createOfferer').its('response.statusCode').should('eq', 201)

  //   // Homepage
  //   cy.url().should('contain', '/accueil')
  // })

  it.skip('should attach user to an existing offerer', () => {
    // TODO: debug and testing-library-ize
    cy.login({
      email: 'retention@example.com',
      password: 'user@AZERTY123',
      redirectUrl: '/parcours-inscription',
    })

    // Welcome page
    cy.contains('Commencer').click()

    // Offerer page
    cy.get('#siret').type(siret)
    cy.wait('@getSiret')
    cy.contains('Continuer').click()
    cy.wait('@getSiret')

    // Offerer attachment
    cy.contains('Rejoindre cet espace').click()

    cy.get('[data-testid="confirm-dialog-button-confirm"]').as(
      'dialogConfirmButton'
    )
    cy.intercept({ method: 'POST', url: '/offerers' }).as('postOfferers')
    cy.get('@dialogConfirmButton').click()
    cy.wait('@postOfferers').its('response.statusCode').should('eq', 201)

    // Confirmation page
    cy.contains('Accéder à votre espace').click()

    // Homepage
    cy.url().should('contain', '/accueil')

    cy.get('#structures')
      .find('option')
      .its('length')
      .then((len) => {
        cy.get('select').select(len - 2)
      })

    cy.contains(
      'Le rattachement à votre structure est en cours de traitement par les équipes du pass Culture'
    ).should('be.visible')
  })
})
