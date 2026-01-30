import {
  DEFAULT_AXE_CONFIG,
  DEFAULT_AXE_RULES,
  MOCKED_BACK_ADDRESS_LABEL,
} from '../support/constants.ts'
import {
  expectOffersOrBookingsAreFound,
  interceptSearch5Adresses,
  sessionLogInAndGoToPage,
} from '../support/helpers.ts'

describe('Create individual offers new flow', () => {
  let login: string

  before(() => {
    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_regular_pro_user_already_onboarded',
      (response) => {
        login = response.body.user.email
      }
    )
  })
  beforeEach(() => {
    // order matters here
    cy.intercept({ method: 'GET', url: '/offers/categories' }).as(
      'getCategories'
    )
    cy.intercept({ method: 'GET', url: '/offers/music-types' }).as(
      'getMusicTypes'
    )
    cy.intercept({ method: 'GET', url: '/offers/*/stocks-stats' }).as(
      'getStocksStats'
    )
    cy.intercept({ method: 'GET', url: '/offers?*' }).as('getOffers')
    cy.intercept({ method: 'GET', url: '/offers/*/stocks/*' }).as('getStocks')

    cy.intercept({ method: 'GET', url: '/offers/*' }).as('getOffer')
    cy.intercept({ method: 'POST', url: '/offers' }).as('postOffer')
    cy.intercept({ method: 'PATCH', url: '/offers/*/stocks' }).as(
      'patchNonEventStocks'
    )
    cy.intercept({ method: 'POST', url: '/stocks/bulk' }).as('postEventStocks')
    cy.intercept({ method: 'PATCH', url: '/offers/publish' }).as('publishOffer')
    cy.intercept({ method: 'GET', url: '/offerers/names' }).as(
      'getOfferersNames'
    )
    cy.intercept({ method: 'PATCH', url: '/offers/*' }).as('patchOffer')
    cy.intercept({ method: 'GET', url: '/offers/categories' }).as(
      'getCategories'
    )
    cy.intercept({ method: 'PUT', url: '/offers/*/price_categories' }).as(
      'replaceOfferPriceCategories'
    )
    cy.intercept({ method: 'GET', url: '/venues?offererId=*' }).as(
      'getVenuesForOfferer'
    )
    interceptSearch5Adresses()

    sessionLogInAndGoToPage(
      'create individual offer new flow',
      login,
      '/offre/individuelle/creation/description'
    )
  })

  it('I should be able to create an individual show offer', () => {
    //  DESCRIPTION STEP
    cy.stepLog({ message: 'I fill in the description' })
    cy.findByLabelText(/Titre de l’offre/).type('Le Diner de Devs')
    cy.wait(['@getCategories', '@getOffer'])
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

    cy.stepLog({ message: 'I validate the description step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@getMusicTypes', '@getOffer', '@postOffer'])

    //  LOCATION STEP
    cy.findByRole('heading', { name: 'Où profiter de l’offre ?' })

    cy.findByLabelText('À une autre adresse').click()
    cy.findByLabelText('Intitulé de la localisation').type(
      'Libellé de mon adresse'
    )
    cy.findByLabelText(/Adresse postale/).type(MOCKED_BACK_ADDRESS_LABEL)
    cy.wait('@search5Address').its('response.statusCode').should('eq', 200)
    cy.findByTestId('list').contains(MOCKED_BACK_ADDRESS_LABEL).click()
    cy.stepLog({ message: 'I validate the location step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@patchOffer'])

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

    cy.findAllByTestId('image-preview').then(($img) => {
      cy.wrap($img)
        .should('be.visible')
        .should('have.prop', 'naturalWidth')
        .and('eq', 470)
      cy.wrap($img)
        .should('be.visible')
        .should('have.prop', 'naturalHeight')
        .and('eq', 705)
    })

    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
    cy.stepLog({ message: 'I validate the media step' })
    cy.findByText('Enregistrer et continuer').click()

    //  PRICE CATEGORIES STEP
    cy.findByLabelText('Intitulé du tarif').should('have.value', 'Tarif unique')
    cy.findByText('Ajouter un tarif').click()
    cy.findByText('Ajouter un tarif').click()
    cy.findByText('Ajouter un tarif').click()

    cy.findAllByLabelText('Intitulé du tarif').eq(0).clear()
    cy.findAllByLabelText('Intitulé du tarif').eq(0).type('Carré Or')
    cy.findAllByLabelText(/Prix/).eq(0).type('100')

    cy.findAllByLabelText('Intitulé du tarif').eq(1).type('Fosse Debout')
    cy.findAllByLabelText(/Prix/).eq(1).type('10')

    cy.findAllByLabelText('Intitulé du tarif').eq(2).type('Fosse Sceptique')
    cy.findAllByRole('checkbox', { name: 'Gratuit' }).eq(2).click()
    // add a price category to delete it later
    cy.findAllByLabelText('Intitulé du tarif').eq(3).type('Prix à supprimer')
    cy.findAllByLabelText(/Prix/).eq(3).type('40')

    cy.findByText('Accepter les réservations “Duo“').should('exist')
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)

    cy.stepLog({ message: 'I validate the price categories step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait('@replaceOfferPriceCategories')

    cy.findAllByText('Définir le calendrier').should('exist')
    // we go back to price categories step to delete a price category
    cy.findByText('Retour').should('exist').should('be.visible').click()
    // we click on delete button of the last price category
    cy.findAllByRole('button', { name: /Supprimer ce tarif/ })
      .eq(3)
      .should('exist')
      .should('be.visible')
      .click()
    cy.findAllByLabelText('Intitulé du tarif').should('have.length', 3)
    cy.stepLog({
      message: 'I validate the price categories step after deletion',
    })
    cy.findByText('Enregistrer et continuer').click()
    // we assert that only 3 priceCategories are present in the response
    cy.wait(['@replaceOfferPriceCategories'])
      .its('response.body.priceCategories')
      .should('have.length', 3)

    //  RECURRENCE FORM DIALOG
    cy.stepLog({ message: 'I fill in the recurrence form' })
    cy.findByRole('button', { name: 'Définir le calendrier' }).click()

    cy.findByText('Toutes les semaines').click()
    cy.findByLabelText('Vendredi').click()
    cy.findByLabelText('Samedi').click()
    cy.findByLabelText('Dimanche').click()
    cy.findByLabelText('Du *').type('2030-05-01')
    cy.findByLabelText('Au *').type('2030-09-30')
    cy.findByLabelText(/Horaire 1/).type('18:30')
    cy.findByText('Ajouter un créneau').click()
    cy.findByLabelText(/Horaire 2/).type('21:00')
    cy.findByText('Ajouter d’autres places et tarifs').click()
    cy.findByText('Ajouter d’autres places et tarifs').click()

    cy.findByTestId('wrapper-quantityPerPriceCategories.0').within(() => {
      cy.findByLabelText(/Tarif/).select('0,00\xa0€ - Fosse Sceptique')
    })

    cy.findAllByLabelText('Nombre de places').eq(0).type('100')

    cy.findByTestId('wrapper-quantityPerPriceCategories.1').within(() => {
      cy.findByLabelText(/Tarif/).select('10,00\xa0€ - Fosse Debout')
    })

    cy.findAllByLabelText('Nombre de places').eq(1).type('20')

    cy.findByTestId('wrapper-quantityPerPriceCategories.2').within(() => {
      cy.findByLabelText(/Tarif/).select('100,00\xa0€ - Carré Or')
    })

    cy.findByLabelText('Nombre de jours avant le début de l’évènement').type(
      '3'
    )

    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
    cy.stepLog({ message: 'I validate the recurrence step' })
    cy.findByText('Valider').click()
    cy.wait(['@postEventStocks', '@getStocks'])

    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
    cy.findByText('Enregistrer et continuer').click()

    //  USEFUL INFORMATIONS STEP
    cy.stepLog({ message: 'I fill in the useful informations' })
    cy.findByText('Retrait sur place (guichet, comptoir...)').click()
    cy.findByLabelText(/Email de contact communiqué aux bénéficiaires/).type(
      'passculture@example.com'
    )

    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
    cy.stepLog({ message: 'I validate the useful information step' })
    cy.findByText('Enregistrer et continuer').click()

    //  SUMMARY STEP
    cy.stepLog({ message: 'I publish my offer' })
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
    cy.findByText('Publier l’offre').click()
    cy.wait(['@getStocksStats', '@getOffer'])

    //  CONFIRMATION STEP
    cy.findByText('Plus tard').click()
    cy.wait(['@publishOffer', '@getOffer'], {
      requestTimeout: 60000 * 2,
      responseTimeout: 60000 * 2,
    })

    //  OFFERS LIST
    cy.stepLog({ message: 'I go to the offers list' })
    cy.findByText('Voir la liste des offres').click()
    cy.wait(['@getOffers', '@getCategories'], {
      requestTimeout: 60 * 1000 * 3,
      responseTimeout: 60 * 1000 * 3,
    })

    cy.stepLog({ message: 'my new offer should be displayed' })
    cy.url().should('contain', '/offres')
    cy.contains('Le Diner de Devs')
    cy.contains('Libellé de mon adresse - 3 RUE DE VALOIS 75008 Paris')
    cy.contains('396 dates')
  })

  it('I should be able to create a physical book individual offer', () => {
    const offerTitle = 'H2G2 Le Guide du voyageur galactique'
    const offerDesc =
      'Une quête pour obtenir la question ultime sur la vie, l’univers et tout le reste.'

    //  DESCRIPTION STEP
    cy.findByLabelText(/Titre de l’offre/).type(offerTitle)
    cy.findByLabelText('Description').type(offerDesc)
    cy.wait(['@getCategories', '@getOffer'])

    // Random 13-digit number because we can't use the same EAN twice
    const ean = String(
      Math.floor(1000000000000 + Math.random() * 9000000000000)
    )
    cy.wrap(ean).as('ean')
    cy.findByLabelText(/Catégorie/).select('Livre')
    cy.findByLabelText(/Sous-catégorie/).select('Livre papier')
    cy.findByLabelText(/Non accessible/).check()
    cy.findByLabelText('Auteur').type('Douglas Adams')
    cy.findByLabelText('EAN-13 (European Article Numbering)').type(ean)

    cy.findByLabelText(/Titre de l’offre/).should('have.value', offerTitle)
    cy.findByLabelText('Description').should('have.text', offerDesc)

    cy.stepLog({ message: 'I validate the description step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@getMusicTypes', '@getOffer', '@postOffer'])

    //  LOCATION STEP
    cy.findByRole('heading', { name: 'Où profiter de l’offre ?' }).should(
      'exist'
    )
    cy.findByLabelText('À une autre adresse').click()
    cy.findByText('Vous ne trouvez pas votre adresse ?').click()
    cy.findByLabelText('Intitulé de la localisation').type(
      'Libellé de mon adresse custom'
    )
    cy.findAllByLabelText(/Adresse postale/)
      .last()
      .type('Place de la gare')
    cy.findAllByLabelText(/Code postal/).type('123123')
    cy.findAllByLabelText(/Ville/).type('Y')
    // eslint-disable-next-line cypress/unsafe-to-chain-command
    cy.findAllByLabelText(/Coordonnées GPS/)
      .type('48.853320, 2.348979')
      .blur()
    cy.findByText('Contrôlez la précision de vos coordonnées GPS.').should(
      'be.visible'
    )

    cy.stepLog({ message: 'I validate offer localisation step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@getOffer', '@patchOffer'], {
      responseTimeout: 60 * 1000 * 2,
    })

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

    cy.stepLog({ message: 'I validate media step' })
    cy.findByText('Enregistrer et continuer').click()

    cy.url().should('contain', '/creation/media')
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@getStocks'], {
      responseTimeout: 60 * 1000 * 2,
    })

    //  STOCKS STEP
    cy.findByLabelText(/Prix/).type('42')
    cy.findByLabelText('Date limite de réservation').type('2042-05-03')
    cy.findByLabelText(/Stock/).type('42')

    cy.stepLog({ message: 'I validate stocks step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@patchNonEventStocks'], {
      responseTimeout: 30 * 1000,
    })

    //  USEFUL INFORMATIONS STEP
    cy.findByLabelText('Informations complémentaires').type(
      'Seuls les dauphins et les souris peuvent le lire.'
    )
    cy.findByText('Être notifié par email des réservations').click()
    cy.stepLog({ message: 'I validate useful information step' })
    cy.findByText('Enregistrer et continuer').click()

    //  SUMMARY STEP
    cy.stepLog({ message: 'I publish my offer' })
    cy.findByText('Publier l’offre').click()
    cy.wait(['@publishOffer', '@getOffer'], {
      requestTimeout: 60000 * 2,
      responseTimeout: 60000 * 2,
    })

    cy.stepLog({ message: 'I go to the offers list' })
    cy.findByText('Voir la liste des offres').click()
    cy.url().should('contain', '/offres')
    cy.wait(['@getOffers', '@getCategories'], {
      requestTimeout: 60 * 1000 * 3,
      responseTimeout: 60 * 1000 * 3,
    })

    //  OFFERS LIST
    cy.stepLog({ message: 'my new offer should be displayed' })
    const expectedNewResults = [
      ['', "Nom de l'offre", 'Lieu', 'Stocks', 'Statut', ''],
      [
        '',
        offerTitle,
        'Libellé de mon adresse custom - Place de la gare 12312 Y',
        '42',
        'publiée',
      ],
      [],
    ]

    expectOffersOrBookingsAreFound(expectedNewResults)
    cy.get('@ean').then((ean) => {
      cy.contains(ean.toString())
    })
  })
})
