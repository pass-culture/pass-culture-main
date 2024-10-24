describe('Signup journey with new venue', () => {
  let login = ''
  const mySiret = '12345678912345'
  const venueName = 'MINISTERE DE LA CULTURE'

  beforeEach(() => {
    cy.visit('/connexion')
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_new_pro_user',
    }).then((response) => {
      login = response.body.user.email
    })
    cy.intercept('GET', `/sirene/siret/**`, (req) =>
      req.reply({
        statusCode: 200,
        body: siretInterceptionPayload(mySiret, venueName),
      })
    ).as('getSiret')
    cy.intercept({
      method: 'GET',
      url: `/venues/siret/**`,
    }).as('venuesSiret')
    cy.intercept(
      'GET',
      'https://api-adresse.data.gouv.fr/search/?limit=1&q=*',
      (req) =>
        req.reply({
          statusCode: 200,
          body: addressInterceptionPayload,
        })
    ).as('search1Address')
    cy.intercept({ method: 'GET', url: '/offerers/names' }).as('getOfferers')
    cy.intercept({
      method: 'GET',
      url: '/venue-types',
      times: 1,
    }).as('venue-types')
    cy.intercept({ method: 'POST', url: '/offerers/new', times: 1 }).as(
      'createOfferer'
    )
  })

  it('Should sign up with a new account, create a new offerer with an unknown SIRET', () => {
    goToOffererCreation(login)

    cy.stepLog({ message: 'I specify a venue with a SIRET' })
    cy.url().should('contain', '/parcours-inscription/structure')
    cy.findByLabelText('Numéro de SIRET à 14 chiffres *').type(mySiret)
    cy.findByText('Continuer').click()
    cy.wait(['@getSiret', '@venuesSiret', '@search1Address']).then(
      (interception) => {
        if (interception[0].response) {
          expect(interception[0].response.statusCode).to.equal(200)
        }
        if (interception[1].response) {
          expect(interception[1].response.statusCode).to.equal(200)
        }
        if (interception[2].response) {
          expect(interception[2].response.statusCode).to.equal(200)
        }
      }
    )

    cy.stepLog({ message: 'I fill identification form with a public name' })
    cy.url().should('contain', '/parcours-inscription/identification')
    cy.findByLabelText('Nom public').type('First Venue')

    cy.findByText('Étape suivante').click()
    cy.wait('@venue-types').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'I fill activity form without target audience' })
    cy.url().should('contain', '/parcours-inscription/activite')
    cy.findByLabelText('Activité principale *').select('Spectacle vivant')
    cy.findByText('Étape suivante').click()
    cy.findByTestId('error-targetCustomer').contains(
      'Veuillez sélectionner une des réponses ci-dessus'
    )

    cy.stepLog({ message: 'an error message is raised' })
    cy.findByTestId('global-notification-error')
      .contains('Une ou plusieurs erreurs sont présentes dans le formulaire')
      .should('not.be.visible')

    cy.stepLog({ message: 'I fill in missing target audience' })
    cy.url().should('contain', '/parcours-inscription/activite')
    cy.findByText('Au grand public').click()
    cy.findByText('Étape suivante').click()

    cy.stepLog({ message: 'the next step is displayed' })
    cy.url().should('contain', '/parcours-inscription/validation')

    cy.stepLog({ message: 'I validate the registration' })

    cy.findByText('Valider et créer ma structure').click()
    cy.wait('@createOfferer')

    cy.stepLog({ message: 'the offerer is created' })
    cy.findAllByTestId('global-notification-success')
      .contains('Votre structure a bien été créée')
      .should('not.be.visible')
    cy.url({ timeout: 10000 }).should('contain', '/accueil')
    cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')

    // TODO: Find a better way to wait for the offerer to be created
    cy.reload()
    cy.wait('@getOfferers').its('response.statusCode').should('eq', 200)
    cy.findByText('First Venue').should('be.visible')
  })
})

describe('Signup journey with known venue', () => {
  let login = ''
  let mySiret: string
  const venueName = 'MINISTERE DE LA CULTURE'

  beforeEach(() => {
    cy.visit('/connexion')
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_new_pro_user_and_offerer',
    }).then((response) => {
      login = response.body.user.email
      mySiret = response.body.siret
    })
    cy.intercept('GET', `/sirene/siret/**`, (req) =>
      req.reply({
        statusCode: 200,
        body: siretInterceptionPayload(mySiret, venueName),
      })
    ).as('getSiret')
    cy.intercept({
      method: 'GET',
      url: `/venues/siret/**`,
    }).as('venuesSiret')
    cy.intercept(
      'GET',
      'https://api-adresse.data.gouv.fr/search/?limit=1&q=*',
      (req) =>
        req.reply({
          statusCode: 200,
          body: addressInterceptionPayload,
        })
    ).as('search1Address')
    cy.intercept(
      'GET',
      'https://api-adresse.data.gouv.fr/search/?limit=5&q=*'
    ).as('search5Address')
    cy.intercept({ method: 'GET', url: '/offerers/names' }).as('getOfferers')
    cy.intercept({
      method: 'GET',
      url: '/venue-types',
      times: 1,
    }).as('venue-types')
    cy.intercept({ method: 'POST', url: '/offerers/new' }).as('createOfferer')
    cy.intercept({ method: 'POST', url: '/offerers' }).as('postOfferers')
  })

  it('Should sign up with a new account and a known offerer, create a new offerer in the space', () => {
    goToOffererCreation(login)

    cy.stepLog({ message: 'I specify an offerer with a SIRET' })
    cy.url().should('contain', '/parcours-inscription/structure')
    cy.findByLabelText('Numéro de SIRET à 14 chiffres *').type(mySiret)
    cy.findByText('Continuer').click()
    cy.wait(['@getSiret', '@venuesSiret', '@search1Address']).then(
      (interception) => {
        if (interception[0].response) {
          expect(interception[0].response.statusCode).to.equal(200)
        }
        if (interception[1].response) {
          expect(interception[1].response.statusCode).to.equal(200)
        }
        if (interception[2].response) {
          expect(interception[2].response.statusCode).to.equal(200)
        }
      }
    )

    cy.stepLog({ message: 'I add a new offerer' })
    cy.url().should('contain', '/parcours-inscription/structure/rattachement')

    cy.findByText('Ajouter une nouvelle structure').click()
    cy.wait('@search5Address')

    cy.stepLog({ message: 'I fill identification form with a new address' })
    cy.url().should('contain', '/parcours-inscription/identification')
    cy.findByLabelText('Adresse postale *').clear()
    cy.findByLabelText('Adresse postale *').invoke(
      'val',
      '89 Rue la Boétie 75008 Pari'
    ) // To avoid being spammed by address search on each chars typed

    cy.findByLabelText('Adresse postale *').type('s') // previous search was too fast, this one raises suggestions
    cy.wait('@search5Address')
    cy.findByRole('option', { name: '89 Rue la Boétie 75008 Paris' }).click()

    cy.findByText('Étape suivante').click()
    cy.wait('@venue-types').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'I fill activity form without main activity' })
    cy.url().should('contain', '/parcours-inscription/activite')
    cy.findByLabelText('Activité principale *').select(
      'Sélectionnez votre activité principale'
    ) // No activity selected
    cy.findByText('Au grand public').click()
    cy.findByText('Étape suivante').click()
    cy.findByTestId('error-venueTypeCode').contains(
      'Veuillez sélectionner une activité principale'
    )

    cy.stepLog({ message: 'an error message is raised' })
    cy.findByTestId('global-notification-error')
      .contains('Une ou plusieurs erreurs sont présentes dans le formulaire')
      .should('not.be.visible')

    cy.stepLog({ message: 'I fill in missing main activity' })
    cy.url().should('contain', '/parcours-inscription/activite')
    cy.findByLabelText('Activité principale *').select('Spectacle vivant')
    cy.findByText('Étape suivante').click()

    cy.stepLog({ message: 'the next step is displayed' })
    cy.url().should('contain', '/parcours-inscription/validation')

    cy.stepLog({ message: 'I validate the registration' })

    cy.findByText('Valider et créer ma structure').click()
    cy.wait('@createOfferer')

    cy.stepLog({ message: 'the offerer is created' })
    cy.findAllByTestId('global-notification-success')
      .contains('Votre structure a bien été créée')
      .should('not.be.visible')
    cy.url({ timeout: 10000 }).should('contain', '/accueil')
    cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')

    // TODO: Find a better way to wait for the offerer to be created
    cy.reload()
    cy.wait('@getOfferers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'the attachment is in progress' })
    cy.contains(
      'Le rattachement à votre structure est en cours de traitement par les équipes du pass Culture'
    ).should('be.visible')
  })

  it('Should sign up with a new account and a known offerer', () => {
    goToOffererCreation(login)

    cy.stepLog({ message: 'I specify an offerer with a SIRET' })
    cy.url().should('contain', '/parcours-inscription/structure')
    cy.findByLabelText('Numéro de SIRET à 14 chiffres *').type(mySiret)
    cy.findByText('Continuer').click()
    cy.wait(['@getSiret', '@venuesSiret', '@search1Address']).then(
      (interception) => {
        if (interception[0].response) {
          expect(interception[0].response.statusCode).to.equal(200)
        }
        if (interception[1].response) {
          expect(interception[1].response.statusCode).to.equal(200)
        }
        if (interception[2].response) {
          expect(interception[2].response.statusCode).to.equal(200)
        }
      }
    )

    cy.stepLog({ message: 'I chose to join the space' })
    cy.contains('Rejoindre cet espace').click()

    cy.findByTestId('confirm-dialog-button-confirm').click()
    cy.wait('@postOfferers').its('response.statusCode').should('eq', 201)
    cy.contains('Accéder à votre espace').click()

    cy.stepLog({ message: 'I am redirected to homepage' })
    cy.url({ timeout: 10000 }).should('contain', '/accueil')
    cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')

    // TODO: Find a better way to wait for the offerer to be created
    cy.reload()
    cy.wait('@getOfferers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'the attachment is in progress' })
    cy.contains(
      'Le rattachement à votre structure est en cours de traitement par les équipes du pass Culture'
    ).should('be.visible')
  })
})

function goToOffererCreation(login: string) {
  const password = 'user@AZERTY123'

  cy.stepLog({ message: 'I am logged in' })
  cy.login({
    email: login,
    password: password,
    redirectUrl: '/',
  })

  cy.stepLog({ message: 'I start offerer creation' })
  cy.findByText('Commencer').click()
}

function siretInterceptionPayload(mySiret: string, venueName: string) {
  return {
    siret: mySiret,
    name: venueName,
    active: true,
    address: {
      street: '3 RUE DE VALOIS',
      postalCode: '75001',
      city: 'Paris',
    },
    ape_code: '90.03A',
    legal_category_code: '1000',
  }
}

const addressInterceptionPayload = {
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
}
