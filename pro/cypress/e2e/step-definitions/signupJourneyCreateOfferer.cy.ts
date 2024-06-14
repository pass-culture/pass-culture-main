import { When, Then, Given } from '@badeball/cypress-cucumber-preprocessor'
const mySiret = '44890182521127' // Math.random().toString().substring(2, 16)
const offererName = 'MINISTERE DE LA CULTURE'

Given('I log in with a {string} new account', (nth: string) => {
  let emailAccount: string // @todo: comptes provisoires avant d'avoir une stratégie de comptes à voir avec Olivier Geber
  switch (nth) {
    case 'first':
      emailAccount = 'pctest.grandpublic.age-more-than-18yo@example.com'
      break
    case 'second':
      emailAccount = 'pctest.autre93.has-signed-up@example.com'
      break
    default:
      emailAccount = 'pctest.autre97.has-signed-up@example.com'
  }
  cy.login({
    email: emailAccount,
    password: 'user@AZERTY123',
    redirectUrl: '/parcours-inscription',
  })

  cy.intercept(
    'GET',
    `https://api-adresse.data.gouv.fr/search/?limit=1&q=3%20RUE%20DE%20VALOIS%20Paris%2075001`,
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
})

When('I start offerer creation', () => {
  cy.findByText('Commencer').click()
})

When('I specify an offerer with a SIRET', () => {
  cy.intercept('GET', `/sirene/siret/${mySiret}`, (req) =>
    req.reply({
      statusCode: 200,
      body: {
        siret: mySiret,
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
  cy.url().should('contain', '/parcours-inscription/structure')
  cy.findByLabelText('Numéro de SIRET à 14 chiffres *').type(mySiret)
  cy.wait('@getSiret').its('response.statusCode').should('eq', 200)
  cy.intercept({
    method: 'GET',
    url: `/venues/siret/${mySiret}`,
  }).as('venues-siret')
  cy.findByText('Continuer').click()
  cy.wait(['@getSiret', '@venues-siret']).then((interception) => {
    if (interception[0].response)
      expect(interception[0].response.statusCode).to.equal(200)
    if (interception[1].response)
      expect(interception[1].response.statusCode).to.equal(200)
  })
})

When('I add details to offerer', () => {
  cy.url().should('contain', '/parcours-inscription/identification')
  cy.findByLabelText('Nom public').type('First Offerer')
  cy.intercept({
    method: 'GET',
    url: '/venue-types',
  }).as('venue-types')
  cy.findByText('Étape suivante').click()
  cy.wait('@venue-types').its('response.statusCode').should('eq', 200)
})

When('I fill activity step', () => {
  cy.url().should('contain', '/parcours-inscription/activite')
  cy.findByLabelText('Activité principale *').select('Spectacle vivant')
  cy.findByLabelText('Site internet, réseau social').type('https://exemple.com')
  cy.findByText('Ajouter un lien').click()
  cy.findAllByTestId('activity-form-social-url')
    .eq(1)
    .type('https://exemple2.com')

  cy.findByText('Au grand public').click()
  cy.findByText('Étape suivante').click()
  // Attente visiblement indispensable, mais venues-types pas toujours reçu si déjà reçu plus haut
  // cy.wait('@venue-types').its('response.statusCode').should('eq', 200)
  cy.wait(1000)
})

When('I validate', () => {
  cy.url().should('contain', '/parcours-inscription/validation')
  cy.intercept({ method: 'POST', url: '/offerers/new' }).as('createOfferer')
  cy.findByText('Valider et créer ma structure').click()
})

When('I add a new offerer', () => {
  cy.url().should('contain', '/parcours-inscription/structure/rattachement')
  cy.findByText('Ajouter une nouvelle structure').click()
})

When('I fill identification step', () => {
  cy.url().should('contain', '/parcours-inscription/identification')
  cy.findByLabelText('Adresse postale *')
    .clear()
    .type('89 Rue la Boétie 75008 Paris')
  cy.findByRole('option', { name: '89 Rue la Boétie 75008 Paris' }).click()

  cy.intercept({
    method: 'GET',
    url: '/venue-types',
  }).as('venue-types')
  cy.findByText('Étape suivante').click()
  cy.wait('@venue-types').its('response.statusCode').should('eq', 200)
})

When('I chose to join the space', () => {
  cy.contains('Rejoindre cet espace').click()

  cy.intercept({ method: 'POST', url: '/offerers' }).as('postOfferers')
  cy.findByTestId('confirm-dialog-button-confirm').click()
  cy.wait('@postOfferers').its('response.statusCode').should('eq', 201)

  // Confirmation page
  cy.contains('Accéder à votre espace').click()
})

When('I am redirected to homepage', () => {
  cy.url().should('contain', '/accueil')
  cy.findByLabelText('Structure').select(offererName)
})

Then('the attachment is in progress', () => {
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
  cy.url().should('contain', '/accueil')
  cy.findAllByTestId('spinner').should('not.exist')

  // check offerer list
  // cy.intercept({ method: 'GET', url: '/offerers/*' }).as('getOfferer')
  cy.findByTestId('offerer-details-offerId').select(offererName)
  // cy.wait('@getOfferer').its('response.statusCode').should('eq', 200)
  cy.findAllByTestId('spinner').should('not.exist')
})
