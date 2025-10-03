import {
  DEFAULT_AXE_CONFIG,
  DEFAULT_AXE_RULES,
  MOCKED_BACK_ADDRESS_LABEL,
} from '../support/constants.ts'
import {
  interceptSearch5Adresses,
  logInAndGoToPage,
} from '../support/helpers.ts'

describe('Create individual offers with OA', () => {
  beforeEach(() => {
    cy.intercept({ method: 'GET', url: '/offers/*' }).as('getOffer')
    cy.intercept({ method: 'POST', url: '/offers/draft' }).as('postOffersDraft')
    cy.intercept({ method: 'PATCH', url: '/offers/*' }).as('patchOffer')
    cy.intercept({ method: 'GET', url: '/offers/*/stocks/*' }).as('getStocks')
    cy.intercept({ method: 'POST', url: '/stocks/bulk' }).as('postEventStocks')
    cy.intercept({ method: 'POST', url: '/stocks' }).as('postProductStock')
    cy.intercept({ method: 'PATCH', url: '/offers/publish' }).as('publishOffer')
    cy.intercept({ method: 'GET', url: '/offers/categories' }).as(
      'getCategories'
    )
    cy.intercept({ method: 'GET', url: '/venues?offererId=*' }).as(
      'getVenuesForOfferer'
    )
    interceptSearch5Adresses()

    cy.wrap(Cypress.session.clearAllSavedSessions())
    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
      (response) => {
        cy.setFeatureFlags([
          { name: 'WIP_ENABLE_NEW_OFFER_CREATION_FLOW', isActive: true },
        ])
        logInAndGoToPage(
          response.body.user.email,
          '/offre/individuelle/creation/description'
        )
      }
    )
  })

  it('I should be able to create a show individual offer', () => {
    const eventName = `Offer with OA (event) ${Cypress.currentRetry + 1}`

    //  DESCRIPTION STEP
    cy.findByLabelText(/Titre de l’offre/).type(eventName)
    cy.findByLabelText('Description').type(
      'Une PO invite des développeurs à dîner...'
    )
    cy.findByLabelText(/Catégorie/).select('Spectacle vivant')
    cy.findByLabelText(/Sous-catégorie/).select('Spectacle, représentation')
    cy.findByLabelText(/Type de spectacle/).select('Théâtre')
    cy.findByLabelText(/Sous-type/).select('Comédie')
    cy.findByLabelText(/Non accessible/).check()
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)

    cy.stepLog({ message: 'I validate offer description step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@getOffer', '@postOffersDraft'])

    //  LOCATION STEP
    cy.findByRole('heading', { name: 'Où profiter de l’offre ?' }).should(
      'exist'
    )
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@getOffer', '@patchOffer'])

    //  MEDIA STEP
    cy.findByLabelText('Importez une image').selectFile(
      'cypress/data/librairie.jpeg',
      {
        force: true,
      }
    )
    cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')
    cy.findByLabelText('Crédit de l’image').type(
      'Les êtres les plus intelligents de l’univers'
    )
    cy.get('input[type=range]').setSliderValue(1.7)
    cy.findByText('Importer').click()

    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)

    cy.stepLog({ message: 'I validate media step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait('@getOffer')

    //  PRICE CATEGORIES STEP
    cy.findByLabelText('Intitulé du tarif').should('have.value', 'Tarif unique')
    cy.findByLabelText(/Prix/).type('100')
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)

    cy.stepLog({ message: 'I validate prices step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@patchOffer', '@getOffer', '@getStocks'], {
      responseTimeout: 60 * 1000 * 3,
    })

    //  RECURRENCE DIALOG
    const fromDate = new Date()
    fromDate.setDate(fromDate.getDate() + 2)
    const fromDateStr = fromDate.toISOString().split('T')[0]
    const toDate = new Date()
    toDate.setDate(toDate.getDate() + 12)
    const toDateStr = toDate.toISOString().split('T')[0]
    cy.findByText('Définir le calendrier').click()
    cy.findByText('Tous les jours').click()
    cy.findByLabelText('Du *').type(fromDateStr)
    cy.findByLabelText('Au *').type(toDateStr)
    cy.findByLabelText(/Horaire 1/).type('18:30')
    cy.findByLabelText(/Tarif/).select('100,00\xa0€ - Tarif unique')

    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
    cy.stepLog({ message: 'I validate recurrence step' })
    cy.findByText('Valider').click()
    cy.wait(['@postEventStocks', '@getStocks', '@getOffer'])
    cy.findByText('11 dates').should('be.visible')
    cy.findByText('Enregistrer et continuer').click()

    //  USEFUL INFORMATIONS STEP
    cy.findByText('Retrait sur place (guichet, comptoir...)').click()
    cy.findByLabelText(/Email de contact communiqué aux bénéficiaires/).type(
      'passculture@example.com'
    )

    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
    cy.stepLog({ message: 'I validate offer useful informations step' })
    cy.findByText('Enregistrer et continuer').click()

    cy.stepLog({ message: 'I publish my offer' })
    cy.findByText('Publier l’offre').click()
    cy.findByText('Plus tard').click()
    cy.wait('@publishOffer', {
      requestTimeout: 60000,
      responseTimeout: 60000,
    })
    cy.wait('@getOffer', { timeout: 60000 })

    //  OFFERS LIST
    cy.stepLog({ message: 'I go to the offers list' })
    cy.findByText('Voir la liste des offres').click()
    cy.wait(['@getOffer', '@getCategories'], {
      requestTimeout: 60 * 1000 * 2,
      responseTimeout: 60 * 1000 * 2,
    })

    cy.stepLog({ message: 'my new offer should be displayed' })
    cy.url().should('contain', '/offres')
    cy.contains(eventName)
    cy.contains('11 dates')

    cy.stepLog({ message: 'I want to update my offer' })
    cy.findAllByText(eventName).eq(1).click()

    //  OFFER LOCATION SUMMARY
    cy.findByRole('link', { name: 'Localisation' }).click()
    cy.url().should('contain', '/localisation')
    cy.contains('Adresse : 1 boulevard Poissonnière 75002 Paris')
    cy.findAllByText('Modifier').eq(1).click()
    cy.url().should('contain', '/edition/localisation')

    //  OFFER LOCATION EDITION
    cy.stepLog({ message: 'I update the OA' })
    cy.findByLabelText('À une autre adresse').click()
    cy.findByLabelText('Intitulé de la localisation').type(
      'Libellé de mon adresse'
    )

    cy.findByLabelText(/Adresse postale/).type(MOCKED_BACK_ADDRESS_LABEL)
    cy.wait('@search5Address').its('response.statusCode').should('eq', 200)
    cy.findByTestId('list').contains(MOCKED_BACK_ADDRESS_LABEL).click()
    cy.findByText('Enregistrer les modifications').click()
    cy.wait(['@getOffer', '@patchOffer'], {
      responseTimeout: 60 * 1000 * 2,
    })
    cy.contains('Intitulé : Libellé de mon adresse')
    cy.contains(`Adresse : 3 RUE DE VALOIS 75008 Paris`)
  })

  it('I should be able to create a physical book individual offer', () => {
    const offerTitle = `Offer with OA (thing) ${Cypress.currentRetry + 1}`
    const offerDesc =
      'Une quête pour obtenir la question ultime sur la vie, l’univers et tout le reste.'

    //  DESCRIPTION STEP
    cy.findByLabelText(/Titre de l’offre/).type(offerTitle)
    cy.findByLabelText('Description').type(offerDesc)

    // Random 13-digit number because we can't use the same EAN twice
    const ean = String(
      Math.floor(1000000000000 + Math.random() * 9000000000000)
    )
    cy.wrap(ean).as('ean')
    cy.findByLabelText(/Catégorie/).select('Livre')
    cy.findByLabelText(/Sous-catégorie/).select('Livre papier')
    cy.findByLabelText('Auteur').type('Douglas Adams')
    cy.findByLabelText('EAN-13 (European Article Numbering)').type(ean)

    cy.findByText('Non accessible').click()

    cy.stepLog({ message: 'I validate offer details step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@postOffersDraft'])

    //  LOCATION STEP
    cy.findByRole('heading', { name: 'Où profiter de l’offre ?' }).should(
      'exist'
    )

    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@getOffer', '@patchOffer'])

    //  MEDIA STEP
    cy.findByLabelText('Importez une image').selectFile(
      'cypress/data/librairie.jpeg',
      {
        force: true,
      }
    )
    cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')
    cy.findByLabelText('Crédit de l’image').type(
      'Les êtres les plus intelligents de l’univers'
    )
    cy.get('input[type=range]').setSliderValue(1.7)
    cy.findByText('Importer').click()

    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)

    cy.stepLog({ message: 'I validate media step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@getOffer', '@getStocks'], {
      responseTimeout: 60 * 1000 * 2,
    })

    //  STOCKS STEP
    cy.findByLabelText(/Prix/).type('42')
    cy.findByLabelText('Date limite de réservation').type('2042-05-03')
    cy.findByLabelText(/Stock/).type('42')

    cy.stepLog({ message: 'I validate stocks step' })
    cy.findByText('Enregistrer et continuer').click()

    cy.wait(['@patchOffer', '@postProductStock', '@getOffer'], {
      requestTimeout: 60 * 1000 * 3,
      responseTimeout: 60 * 1000 * 3,
    })

    //  USEFUL INFORMATIONS STEP
    cy.findByLabelText('Informations complémentaires').type(
      'Seuls les dauphins et les souris peuvent le lire.'
    )
    cy.findByText('Être notifié par email des réservations').click()

    cy.stepLog({ message: 'I validate offer useful informations step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@getOffer', '@patchOffer'], {
      responseTimeout: 60 * 1000,
    })

    cy.stepLog({ message: 'I publish my offer' })
    cy.findByText('Publier l’offre').click()
    cy.wait(['@publishOffer', '@getOffer'], {
      requestTimeout: 60000 * 2,
      responseTimeout: 60000 * 2,
    })
    cy.findByText('Plus tard').click()

    //  OFFERS LIST
    cy.stepLog({ message: 'I go to the offers list' })
    cy.findByText('Voir la liste des offres').click()
    cy.url().should('contain', '/offres')
    cy.wait(['@getOffer', '@getCategories'], {
      requestTimeout: 60 * 1000 * 2,
      responseTimeout: 60 * 1000 * 2,
    })

    cy.stepLog({ message: 'my new offer should be displayed' })
    cy.contains(offerTitle)
    cy.get('@ean').then((ean) => {
      cy.contains(ean.toString())
    })

    cy.stepLog({ message: 'I want to update my offer' })
    cy.findAllByText(offerTitle).eq(1).click()

    //  OFFER LOCATION SUMMARY
    cy.findByRole('link', { name: 'Localisation' }).click()
    cy.url().should('contain', '/localisation')
    cy.contains('Adresse : 1 boulevard Poissonnière 75002 Paris')
    cy.findAllByText('Modifier').eq(1).click()
    cy.url().should('contain', '/edition/localisation')

    //  OFFER LOCATION EDITION
    cy.stepLog({ message: 'I update the OA' })
    cy.findByLabelText('À une autre adresse').click()
    cy.findByText('Vous ne trouvez pas votre adresse ?').click()
    cy.findByLabelText('Intitulé de la localisation').type(
      'Libellé de mon adresse custom'
    )

    cy.stepLog({ message: 'I want to put a custom address' })
    cy.findAllByLabelText(/Adresse postale/)
      .last()
      .type('Place de la gare')
    cy.findAllByLabelText(/Code postal/).type('123123')
    cy.findAllByLabelText(/Ville/).type('Y')
    // eslint-disable-next-line cypress/unsafe-to-chain-command
    cy.findAllByLabelText(/Coordonnées GPS/)
      .type('48.853320, 2.348979')
      .blur()
    cy.findByText('Vérifiez la localisation en cliquant ici').should(
      'be.visible'
    )
    cy.findByText('Enregistrer les modifications').click()
    cy.wait(['@getOffer', '@patchOffer'], {
      responseTimeout: 60 * 1000 * 2,
    })
    cy.contains('Intitulé : Libellé de mon adresse custom')
    cy.contains('Adresse : Place de la gare 12312 Y')
  })
})
