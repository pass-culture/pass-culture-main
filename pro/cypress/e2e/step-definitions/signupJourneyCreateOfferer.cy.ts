import { When, Then, Given } from '@badeball/cypress-cucumber-preprocessor'
const siret = Math.random().toString().substring(2, 16)
const offererName = 'MINISTERE DE LA CULTURE'

beforeEach(() => {
  cy.intercept({
    method: 'GET',
    url: '/venue-types',
  }).as('venue-types')

  cy.intercept('GET', `http://localhost:5001/sirene/siret/${siret}`, (req) =>
    req.reply({
      statusCode: 200,
      body: {
        siret: siret,
        name: offererName,
        active: true,
        address: {
          street: '89 Rue la Boétie 75008 Paris',
          postalCode: '75008',
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
  ).as('searchAddress')

  // cy.intercept(
  //   'GET',
  //   `https://api-adresse.data.gouv.fr/search/?limit=5&q=89%20Rue%20la%20Bo%C3%A9tie%2075008%20Paris`,
  //   (req) =>
  //     req.reply({
  //       statusCode: 200,
  //       body: {
  //         type: 'FeatureCollection',
  //         version: 'draft',
  //         features: [
  //           {
  //             type: 'Feature',
  //             geometry: {
  //               type: 'Point',
  //               coordinates: [2.308289, 48.87171],
  //             },
  //             properties: {
  //               label: '89 Rue la Boétie 75008 Paris',
  //               score: 0.97351,
  //               housenumber: '89',
  //               id: '75108_5194_00089',
  //               name: '89 Rue la Boétie',
  //               postcode: '75008',
  //               citycode: '75108',
  //               x: 649261.94,
  //               y: 6863742.69,
  //               city: 'Paris',
  //               district: 'Paris 8e Arrondissement',
  //               context: '75, Paris, Île-de-France',
  //               type: 'housenumber',
  //               importance: 0.70861,
  //               street: 'Rue la Boétie',
  //             },
  //           },
  //           // {
  //           //   type: 'Feature',
  //           //   geometry: {
  //           //     type: 'Point',
  //           //     coordinates: [2.306726, 48.870711],
  //           //   },
  //           //   properties: {
  //           //     label: 'Galerie Elysées-la Boétie 75008 Paris',
  //           //     score: 0.49326529933481156,
  //           //     id: '75108_3191',
  //           //     name: 'Galerie Elysées-la Boétie',
  //           //     postcode: '75008',
  //           //     citycode: '75108',
  //           //     x: 649146.32,
  //           //     y: 6863632.62,
  //           //     city: 'Paris',
  //           //     district: 'Paris 8e Arrondissement',
  //           //     context: '75, Paris, Île-de-France',
  //           //     type: 'street',
  //           //     importance: 0.59665,
  //           //     street: 'Galerie Elysées-la Boétie',
  //           //   },
  //           // },
  //         ],
  //         attribution: 'BAN',
  //         licence: 'ETALAB-2.0',
  //         query: '89 Rue la Boétie 75008 Paris',
  //         limit: 5,
  //       },
  //     })
  // )
})

Given('I log in with an EAC account', () => {
  cy.login({
    email: 'eac_1_lieu@example.com',
    password: 'user@AZERTY123',
    redirectUrl: '/parcours-inscription',
  })
})

Given('I log in with a retention account', () => {
  cy.login({
    email: 'retention@example.com',
    password: 'user@AZERTY123',
    redirectUrl: '/parcours-inscription',
  })
})

Given('I log in with another retention account', () => {
  cy.login({
    email: 'retention_structures@example.com',
    password: 'user@AZERTY123',
    redirectUrl: '/parcours-inscription',
  })
})

When('I create a new offerer with a SIRET', () => {
  cy.findByText('Commencer').click()

  // Offerer/Structure page
  cy.url().should('contain', '/parcours-inscription/structure')
  cy.findByLabelText('Numéro de SIRET à 14 chiffres *').type(siret)
  cy.wait('@getSiret').its('response.statusCode').should('eq', 200)
  cy.findByText('Continuer').click()
  cy.wait('@getSiret').its('response.statusCode').should('eq', 200)

  // Authentication page
  cy.url().should('contain', '/parcours-inscription/identification')
  cy.findByLabelText('Nom public').type('First Offerer')
  cy.findByText('Étape suivante').click()
  cy.wait('@venue-types').its('response.statusCode').should('eq', 200)

  // Activity page
  cy.url().should('contain', '/parcours-inscription/activite')
  cy.findByLabelText('Activité principale *').select('Spectacle vivant')
  cy.findByLabelText('Site internet, réseau social').type('https://exemple.com')
  cy.findByText('Ajouter un lien').click()
  cy.findAllByTestId('activity-form-social-url')
    .eq(1)
    .type('https://exemple2.com')

  cy.findByText('Au grand public').click()
  cy.findByText('Étape suivante').click()

  // Validation page
  cy.url().should('contain', '/parcours-inscription/validation')
  cy.intercept({ method: 'POST', url: '/offerers/new' }).as('createOfferer')
  cy.findByText('Valider et créer ma structure').click()
})

When('I ask for an offerer attachment', () => {
  // Welcome page
  cy.findByText('Commencer').click()

  // Offerer/Structure page
  cy.url().should('contain', '/parcours-inscription/structure')
  cy.findByLabelText('Numéro de SIRET à 14 chiffres *').type(siret)
  cy.wait('@getSiret').its('response.statusCode').should('eq', 200)
  cy.findByText('Continuer').click()
  cy.wait('@getSiret').its('response.statusCode').should('eq', 200)

  // Offerer attachment
  cy.url().should('contain', '/parcours-inscription/structure/rattachement')
  cy.findByText('Ajouter une nouvelle structure').click()
  cy.wait('@venue-types').its('response.statusCode').should('eq', 200)

  // Authentication page
  cy.url().should('contain', '/parcours-inscription/identification')
  cy.findByLabelText('Adresse postale *')
    .clear()
    .type('89 Rue la Boétie 75008 Paris')
  cy.findByRole('option', { name: '89 Rue la Boétie 75008 Paris' }).click()

  cy.findByText('Étape suivante').click()
  cy.wait('@venue-types').its('response.statusCode').should('eq', 200)

  // Activity page
  cy.url().should('contain', '/parcours-inscription/activite')
  cy.findByLabelText('Activité principale *').select('Spectacle vivant')

  cy.findByText('Au grand public').click()
  cy.findByText('Étape suivante').click()

  // Validation page
  cy.url().should('contain', '/parcours-inscription/validation')
  cy.intercept({ method: 'POST', url: '/offerers/new' }).as('createOfferer')
  cy.findByText('Valider et créer ma structure').click()
})

When('I ask to join a space', () => {
  // Welcome page
  cy.findByText('Commencer').click()

  // Offerer/Structure page
  cy.url().should('contain', '/parcours-inscription/structure')
  cy.findByLabelText('Numéro de SIRET à 14 chiffres *').type(siret)
  cy.wait('@getSiret').its('response.statusCode').should('eq', 200)
  cy.findByText('Continuer').click()
  cy.wait('@getSiret').its('response.statusCode').should('eq', 200)

  // Offerer attachment
  cy.contains('Rejoindre cet espace').click()

  //   cy.get('[data-testid="confirm-dialog-button-confirm"]').as(
  //     'dialogConfirmButton'
  //   )
  cy.intercept({ method: 'POST', url: '/offerers' }).as('postOfferers')
  //   cy.get('@dialogConfirmButton').click()
  cy.findByTestId('confirm-dialog-button-confirm').click()
  cy.wait('@postOfferers').its('response.statusCode').should('eq', 201)

  // Confirmation page
  cy.contains('Accéder à votre espace').click()

  // Homepage
  cy.url().should('contain', '/accueil')

  // cy.get('#structures') // @todo
  //   .find('option')
  //   .its('length')
  //   .then((len) => {
  //     cy.get('select').select(len - 2)
  //   })
  cy.findByLabelText('Structure').select(offererName)
})

Then('the rattachment is in progress', () => {
  cy.contains(
    'Le rattachement à votre structure est en cours de traitement par les équipes du pass Culture'
  ).should('be.visible')
})

Then('the offerer is created', () => {
  cy.wait('@createOfferer').its('response.statusCode').should('eq', 201)
  cy.findAllByTestId('global-notification-success').should(
    'contain',
    'Votre structure a bien été créée'
  )
  cy.reload()
  cy.url().should('contain', '/accueil')
  cy.findAllByTestId('spinner').should('exist')
  cy.findAllByTestId('spinner').should('not.exist')

  // check offerer list
  cy.intercept({
    method: 'GET',
    url: '/offerers/**',
  }).as('offerersItem')
  cy.findByTestId('offerer-details-offerId').select(offererName)
  cy.findAllByTestId('spinner').should('not.exist')
  cy.wait('@offerersItem').its('response.statusCode').should('eq', 200)
})
