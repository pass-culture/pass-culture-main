describe('Create an individual offer (thing)', () => {
  before(async () => {
    await fetch('http://localhost:5001/e2e/pro/create-event-individual-offer').then(res => res.stat)
  })
  it('should create an individual offer', () => {
    cy.setFeatureFlags([{ name: 'WIP_ENABLE_PRO_SIDE_NAV', isActive: false }])

    // Random 13-digit number because we can't use the same EAN twice
    const ean = String(
      Math.floor(1000000000000 + Math.random() * 9000000000000)
    )
    cy.login({
      email: 'pro_adage_eligible@example.com',
      password: 'user@AZERTY123',
    })

    // Go to offer creation page
    cy.contains('Créer une offre').click()

    // Select an offer type
    cy.contains('Au grand public').click()
    cy.contains('Un bien physique').click()

    cy.intercept({ method: 'GET', url: '/offers/categories' }).as(
      'getCategories'
    )
    cy.contains('Étape suivante').click()
    cy.wait('@getCategories')

    // Fill in first step: offer details
    cy.get('#categoryId').select('Livre')
    cy.get('#subcategoryId').select('Livre papier')
    cy.get('#name').type('H2G2 Le Guide du voyageur galactique')
    cy.get('#description').type(
      'Une quête pour obtenir la question ultime sur la vie, l’univers et tout le reste.'
    )
    cy.get('#author').type('Douglas Adams')
    cy.get('#ean').type(ean)

    cy.contains('Ajouter une image').click()
    cy.get('input[type=file]').selectFile('cypress/e2e/offer-image.jpg', {
      force: true,
    })
    cy.get('#credit').type('Les êtres les plus intelligents de l’univers')
    cy.contains('Suivant').click()
    cy.get('[role="dialog"]').contains('Enregistrer').click()

    cy.get('#withdrawalDetails').type(
      'Seuls les dauphins et les souris peuvent le lire.'
    )
    cy.contains('Psychique ou cognitif').click()
    cy.contains('Moteur').click()
    cy.contains('Auditif').click()
    cy.get('#externalTicketOfficeUrl').type('https://passculture.app/')

    cy.contains('Être notifié par email des réservations').click()

    cy.intercept({ method: 'POST', url: '/offers' }).as('postOffer')
    cy.intercept({ method: 'GET', url: '/offers/*' }).as('getOffer')
    cy.contains('Enregistrer et continuer').click()
    cy.wait(['@postOffer', '@getOffer'])

    // Fill in second step: stocks
    cy.get('#price').type('42')
    cy.get('#bookingLimitDatetime').type('2042-05-03')
    cy.get('#quantity').type('42')

    cy.intercept({ method: 'PATCH', url: '/offers/*' }).as('patchOffer')
    cy.intercept({ method: 'POST', url: '/stocks/bulk' }).as('postStocks')
    cy.contains('Enregistrer et continuer').click()
    cy.wait(['@patchOffer', '@postStocks', '@getOffer'])

    // Publish offer
    cy.contains('Livre papier')
    cy.intercept({ method: 'PATCH', url: '/offers/publish' }).as('publishOffer')
    cy.contains('Publier l’offre').click()
    cy.wait(['@publishOffer', '@getOffer'])

    // Go to offer list and check that the offer is there
    cy.intercept({ method: 'GET', url: '/offers' }).as('getOffers')
    cy.contains('Voir la liste des offres').click()
    cy.wait('@getOffers')
    cy.contains('H2G2 Le Guide du voyageur galactique')
    cy.contains(ean)
  })
})
