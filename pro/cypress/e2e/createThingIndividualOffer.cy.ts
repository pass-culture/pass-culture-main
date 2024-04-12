// what is a thing? une chose?
describe('Create an individual offer (thing)', () => {
  it('should create an individual offer', () => {
    // toujours d'actu ce flag? où aller voir pour savoir?    
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
    cy.findByText('Créer une offre').click()

    // Select an offer type
    cy.findByText('Au grand public').click()
    cy.findByText('Un bien physique').click()

    cy.intercept({ method: 'GET', url: '/offers/categories' }).as(
      'getCategories'
    )
    cy.findByText('Étape suivante').click()
    cy.wait('@getCategories')

    // Fill in first step: offer details
    cy.findByLabelText('Catégorie *').select('Livre')
    cy.findByLabelText('Sous-catégorie *').select('Livre papier')
    cy.findByLabelText('Titre de l’offre *').type('H2G2 Le Guide du voyageur galactique')
    cy.findByLabelText('Description').type(
      'Une quête pour obtenir la question ultime sur la vie, l’univers et tout le reste.'
    )
    cy.findByLabelText('Auteur').type('Douglas Adams')
    cy.findByLabelText('EAN-13 (European Article Numbering)').type(ean)
    cy.findByText('Ajouter une image').click()
    cy.get('input[type=file]').selectFile('cypress/e2e/offer-image.jpg', {
      force: true,
    })
    cy.findByLabelText('Crédit de l’image').type('Les êtres les plus intelligents de l’univers')
    cy.findByText('Suivant').click()
    cy.findByText('Enregistrer').click()

    cy.findByLabelText('Informations de retrait').type(
      'Seuls les dauphins et les souris peuvent le lire.'
    )
    cy.findByText('Non accessible').click()
    cy.findByText('Psychique ou cognitif').click()
    cy.findByText('Moteur').click()
    cy.findByText('Auditif').click()
    cy.get('#externalTicketOfficeUrl').type('https://passculture.app/')

    cy.findByText('Être notifié par email des réservations').click()

    cy.intercept({ method: 'POST', url: '/offers' }).as('postOffer')
    cy.intercept({ method: 'GET', url: '/offers/*' }).as('getOffer')
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@postOffer', '@getOffer'])

    // Fill in second step: stocks
    cy.get('#price').type('42')
    cy.get('#bookingLimitDatetime').type('2042-05-03')
    cy.get('#quantity').type('42')

    cy.intercept({ method: 'PATCH', url: '/offers/*' }).as('patchOffer')
    cy.intercept({ method: 'POST', url: '/stocks/bulk' }).as('postStocks')
    cy.intercept({ method: 'GET', url: '/offers/*' }).as('getOffer')
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@patchOffer', '@postStocks', '@getOffer'])

    // Publish offer
    cy.findByText('Livre papier').should('exist')
    cy.intercept({ method: 'PATCH', url: '/offers/publish' }).as('publishOffer')
    cy.findByText('Publier l’offre').click()
    cy.wait(['@publishOffer', '@getOffer'])

    // Go to offer list and check that the offer is there
    cy.intercept({ method: 'GET', url: '/offers' }).as('getOffers')
    cy.findByText('Voir la liste des offres').click()
    cy.wait('@getOffers')
    // findByText() passe pas ici, je n'ai pas compris pourquoi
    cy.contains('H2G2 Le Guide du voyageur galactique')
    cy.contains(ean)
  })
})
