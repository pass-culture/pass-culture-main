import { Given, Then, When } from '@badeball/cypress-cucumber-preprocessor'

const mySiret = '44890182521127'
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
})

When('I start offerer creation', () => {
  cy.findByText('Commencer').click()
})

When('I specify an offerer with a SIRET', () => {
  cy.url().should('contain', '/parcours-inscription/structure')
  cy.findByLabelText('Numéro de SIRET à 14 chiffres *').type(mySiret)
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
  cy.intercept({
    method: 'GET',
    url: `/venues/siret/${mySiret}`,
  }).as('venuesSiret')

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
})

When('I fill activity form without main activity', () => {
  cy.url().should('contain', '/parcours-inscription/activite')
  cy.findByLabelText('Activité principale *').select(
    'Sélectionnez votre activité principale'
  ) // No activity selected
  cy.findByText('Au grand public').click()
  cy.findByText('Étape suivante').click()
  cy.findByTestId('error-venueTypeCode').contains(
    'Veuillez sélectionner une activité principale'
  )
})

When('I fill activity form without target audience', () => {
  cy.url().should('contain', '/parcours-inscription/activite')
  cy.findByLabelText('Activité principale *').select('Spectacle vivant')
  cy.findByText('Étape suivante').click()
  cy.findByTestId('error-targetCustomer').contains(
    'Veuillez sélectionner une des réponses ci-dessus'
  )
})

When('I validate the registration', () => {
  cy.wait(2000) // @todo: delete this when random failures fixed
  cy.findByText('Valider et créer ma structure').click()
})

When('I add a new offerer', () => {
  cy.url().should('contain', '/parcours-inscription/structure/rattachement')
  cy.findByText('Ajouter une nouvelle structure').click()
  cy.wait('@search5Address')
})

When('I fill identification form with a new address', () => {
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
})

When('I fill identification form with a public name', () => {
  cy.url().should('contain', '/parcours-inscription/identification')
  cy.findByLabelText('Nom public').type('First Offerer')

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
  cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')

  cy.findByTestId('offerer-details-offerId').select(offererName)
  cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')
})

Then('An error message is raised', () => {
  cy.findByTestId('global-notification-error').contains(
    'Une ou plusieurs erreurs sont présentes dans le formulaire'
  )
  cy.url().should('not.contain', '/parcours-inscription/validation')
})

Then('The next step is displayed', () => {
  cy.url().should('contain', '/parcours-inscription/validation')
})

When('I fill in missing main activity', () => {
  cy.url().should('contain', '/parcours-inscription/activite')
  cy.findByLabelText('Activité principale *').select('Spectacle vivant')
  cy.findByText('Étape suivante').click()
})

When('I fill in missing target audience', () => {
  cy.url().should('contain', '/parcours-inscription/activite')
  cy.findByText('Au grand public').click()
  cy.findByText('Étape suivante').click()
})
