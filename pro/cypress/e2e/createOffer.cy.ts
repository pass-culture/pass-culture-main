describe('Create an individual offer', () => {
  it('should create an individual offer', () => {
    cy.login('pctest.admin93.0@example.com', 'user@AZERTY123')

    // Go to offer creation page
    cy.intercept({ method: 'GET', url: '/offerers/*/eac-eligibility' }).as(
      'getEacEligibility'
    )
    cy.contains('Créer une offre').click()
    cy.wait('@getEacEligibility')

    // Select an offer type
    cy.contains('Au grand public').click()
    cy.contains('Un évènement physique daté').click()

    cy.intercept({ method: 'GET', url: '/offers/categories' }).as(
      'getCategories'
    )
    cy.contains('Étape suivante').click()
    cy.wait('@getCategories')

    // Fill in first step: offer details
    cy.get('#categoryId').select('Spectacle vivant')
    cy.get('#subcategoryId').select('Spectacle, représentation')
    cy.get('#showType').select('Théâtre')
    cy.get('#showSubType').select('Comédie')
    cy.get('#name').type('Le Diner de Devs')
    cy.get('#description').type('Une PO invite des développeurs à dîner...')
    cy.contains('Retrait sur place').click()
    cy.get('#bookingContact').type('passculture@example.com')

    cy.intercept({ method: 'POST', url: '/offers' }).as('postOffer')
    cy.intercept({ method: 'GET', url: '/offers/*' }).as('getOffer')
    cy.contains('Étape suivante').click()
    cy.wait(['@postOffer', '@getOffer'])

    // Fill in second step: price categories
    cy.contains('Ajouter un tarif').click()
    cy.contains('Ajouter un tarif').click()
    cy.get('[name="priceCategories[0].label"]').type('Carré Or')
    cy.get('[name="priceCategories[0].price"]').type('100')
    cy.get('[name="priceCategories[1].label"]').type('Fosse Debout')
    cy.get('[name="priceCategories[1].price"]').type('10')
    cy.get('[name="priceCategories[2].label"]').type('Fosse Sceptique')
    cy.get('[name="priceCategories[2].free"]').click()

    cy.intercept({ method: 'PATCH', url: '/offers/*' }).as('patchOffer')
    cy.contains('Étape suivante').click()
    cy.wait(['@patchOffer', '@getOffer'])

    // Fill in third step: recurrence
    cy.contains('Ajouter une ou plusieurs dates').click()
    cy.contains('Toutes les semaines').click()
    cy.get('[aria-label="Vendredi"]').click()
    cy.get('[aria-label="Samedi"]').click()
    cy.get('[aria-label="Dimanche"]').click()
    cy.get('#startingDate').type('2030-05-01')
    cy.get('#endingDate').type('2030-09-30')
    cy.get('[name="beginningTimes[0]"]').type('18:30')
    cy.contains('Ajouter un créneau').click()
    cy.get('[name="beginningTimes[1]"]').type('21:00')
    cy.contains('Ajouter d’autres places et tarifs').click()
    cy.contains('Ajouter d’autres places et tarifs').click()
    cy.get('[name="quantityPerPriceCategories[0].priceCategory"]').select(
      '0 € - Fosse Sceptique'
    )
    cy.get('[name="quantityPerPriceCategories[1].quantity"]').type('100')
    cy.get('[name="quantityPerPriceCategories[1].priceCategory"]').select(
      '10 € - Fosse Debout'
    )
    cy.get('[name="quantityPerPriceCategories[2].quantity"]').type('20')
    cy.get('[name="quantityPerPriceCategories[2].priceCategory"]').select(
      '100 € - Carré Or'
    )
    cy.get('#bookingLimitDateInterval').type('3')
    cy.contains('Valider').click()

    cy.intercept({ method: 'POST', url: '/stocks/bulk' }).as('postStocks')
    cy.contains('Étape suivante').click()
    cy.wait(['@postStocks', '@getOffer'])

    // Publish offer
    cy.intercept({ method: 'PATCH', url: '/offers/publish' }).as('publishOffer')
    cy.contains('Publier l’offre').click()
    cy.wait(['@publishOffer', '@getOffer'])

    // Go to offer list and check that the offer is there
    cy.intercept({ method: 'GET', url: '/offers' }).as('getOffers')
    cy.contains('Voir la liste des offres').click()
    cy.wait('@getOffers')
    cy.contains('Le Diner de Devs')
    cy.contains('396 dates')
  })
})
