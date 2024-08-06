import { Then, When } from '@badeball/cypress-cucumber-preprocessor'

When('I fill in details for physical offer', () => {
  cy.setFeatureFlags([{ name: 'WIP_SPLIT_OFFER', isActive: true }])
  cy.findByLabelText('Titre de l’offre *').type(
    'H2G2 Le Guide du voyageur galactique'
  )
  cy.findByLabelText('Description').type(
    'Une quête pour obtenir la question ultime sur la vie, l’univers et tout le reste.'
  )
  // Random 13-digit number because we can't use the same EAN twice
  const ean = String(Math.floor(1000000000000 + Math.random() * 9000000000000))
  cy.wrap(ean).as('ean')
  cy.findByLabelText('Catégorie *').select('Livre')
  cy.findByLabelText('Sous-catégorie *').select('Livre papier')
  cy.findByLabelText('Auteur').type('Douglas Adams')
  cy.findByLabelText('EAN-13 (European Article Numbering)').type(ean)
  cy.findByText('Ajouter une image').click()
  cy.get('input[type=file]').selectFile('cypress/data/offer-image.jpg', {
    force: true,
  })
  cy.findByLabelText('Crédit de l’image').type(
    'Les êtres les plus intelligents de l’univers'
  )
  cy.findByText('Suivant').click()
  cy.findByText('Enregistrer').click()
})

When('I fill in useful informations for physical offer', () => {
  cy.findByLabelText('Informations de retrait').type(
    'Seuls les dauphins et les souris peuvent le lire.'
  )
  cy.findByText('Non accessible').click()
  cy.findByText('Psychique ou cognitif').click()
  cy.findByText('Moteur').click()
  cy.findByText('Auditif').click()
  cy.get('#externalTicketOfficeUrl').type('https://passculture.app/')

  cy.findByText('Être notifié par email des réservations').click()
})

When('I fill in stocks', () => {
  cy.get('#price').type('42')
  cy.get('#bookingLimitDatetime').type('2042-05-03')
  cy.get('#quantity').type('42')
})

When('I validate stocks step', () => {
  cy.intercept({ method: 'PATCH', url: '/offers/*', times: 1 }).as('patchOffer')
  cy.intercept({ method: 'POST', url: '/stocks/bulk' }).as('postStocks')
  cy.intercept({ method: 'GET', url: '/offers/*' }).as('getOffer')
  cy.findByText('Enregistrer et continuer').click()
  cy.wait(['@patchOffer', '@postStocks', '@getOffer'], {
    responseTimeout: 30 * 1000,
  })
})

When('I go to my offers list', () => {
  // There is an issue with the api being slow here. Wait for everything for now.
  cy.intercept({ method: 'GET', url: '/offers?*' }).as('getOffersForOfferer')
  cy.intercept({ method: 'GET', url: '/offerers/names' }).as('getOffererNames')
  cy.intercept({ method: 'GET', url: '/offerers/*' }).as('getOfferer')
  cy.intercept({ method: 'GET', url: '/venues*' }).as('getVenue')
  cy.findByText('Voir la liste des offres').click()
  cy.wait('@getVenue', {
    timeout: 60 * 1000,
  })
  cy.wait('@getOffersForOfferer', {
    timeout: 60 * 1000,
  })
  cy.wait(['@getCategories', '@getOfferer', '@getOffererNames'], {
    requestTimeout: 60 * 1000 * 3,
    responseTimeout: 60 * 1000 * 3,
  })
})

Then('my new physical offer should be displayed', () => {
  cy.contains('H2G2 Le Guide du voyageur galactique')
  cy.get('@ean').then((ean) => {
    cy.contains(ean.toString())
  })
})

When('I validate offer details step', () => {
  cy.intercept({ method: 'GET', url: '/offers/*' }).as('getOffer')
  cy.intercept({ method: 'POST', url: '/offers/draft' }).as('postDraftOffer')

  cy.findByText('Enregistrer et continuer').click()
  cy.wait(['@getOffer', '@postDraftOffer'])
})

When('I validate offer useful informations step', () => {
  cy.intercept({ method: 'GET', url: '/offers/*' }).as('getOffer')
  cy.intercept({ method: 'PATCH', url: '/offers/*', times: 1 }).as('patchOffer')
  cy.findByText('Enregistrer et continuer').click()
  cy.wait(['@getOffer', '@patchOffer'])
})
