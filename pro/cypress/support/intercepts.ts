beforeEach(() => {
  cy.intercept({
    method: 'GET',
    url: '/adage-iframe/playlists/local-offerers',
  }).as('local_offerers')
  cy.intercept({
    method: 'GET',
    url: '/adage-iframe/collective/offers-template/**',
  }).as('offers_template')
  cy.intercept({
    method: 'POST',
    url: '/adage-iframe/logs/fav-offer/',
  }).as('fav-offer')
  cy.intercept({
    method: 'DELETE',
    url: '/adage-iframe/collective/template/**/favorites',
  }).as('delete_fav')
  cy.intercept(
    'GET',
    'https://api-adresse.data.gouv.fr/search/?limit=1&q=*'
  ).as('search1Address')
  cy.intercept(
    'GET',
    'https://api-adresse.data.gouv.fr/search/?limit=5&q=*'
  ).as('search5Address')
  cy.intercept({
    method: 'GET',
    url: 'https://api-adresse.data.gouv.fr/search/?limit=5&q=89%20Rue%20la%20Bo%C3%A9tie%2075008%20Paris',
  }).as('searchAddress')
  cy.intercept({ method: 'GET', url: '/collective/offers*' }).as(
    'collectiveOffers'
  )
  cy.intercept({
    method: 'GET',
    url: '/features',
  }).as('features')
  cy.intercept({ method: 'POST', url: '/offers' }).as('postOffer')
  cy.intercept({ method: 'GET', url: '/offers/names' }).as('getOffersNames')
  cy.intercept({ method: 'GET', url: '/offers/categories' }).as('getCategories')
  cy.intercept({ method: 'GET', url: '/offers/*/stocks/*' }).as('getStocks')
  cy.intercept({ method: 'GET', url: '/offers/*' }).as('getOffer')
  cy.intercept({ method: 'GET', url: '/offers?offererId=?' }).as(
    'getOffersForProvider'
  )
  cy.intercept({ method: 'POST', url: '/offerers/new' }).as('createOfferer')
  cy.intercept({ method: 'PATCH', url: '/offers/*' }).as('patchOffer')
  cy.intercept({ method: 'POST', url: '/stocks/bulk' }).as('postStocks')
  cy.intercept({ method: 'GET', url: '/venues?offererId=*' }).as(
    'getVenuesForOfferer'
  )
  cy.intercept({
    method: 'GET',
    url: '/venue-types',
  }).as('venue-types')
  cy.intercept({ method: 'POST', url: '/venues' }).as('postVenues')
  cy.intercept({ method: 'GET', url: '/venues*' }).as('getVenue')
  cy.intercept({ method: 'PATCH', url: '/venues/*' }).as('patchVenue')
  cy.intercept({ method: 'POST', url: '/v2/users/signup/pro' }).as('signupUser')
})
