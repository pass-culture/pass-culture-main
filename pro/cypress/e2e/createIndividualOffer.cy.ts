import { DEFAULT_AXE_CONFIG, DEFAULT_AXE_RULES } from '../support/constants.ts'
import {
  expectOffersOrBookingsAreFoundForNewTable,
  interceptSearch5Adresses,
  logInAndGoToPage,
} from '../support/helpers.ts'

describe('Create individual offers', { testIsolation: false }, () => {
  let venueName: string
  const stock = '42'

  beforeEach(() => {
    cy.intercept({ method: 'GET', url: '/offers/*' }).as('getOffer')
    cy.intercept({ method: 'POST', url: '/offers/draft' }).as('postDraftOffer')
    cy.intercept({ method: 'PATCH', url: '/offers/*' }).as('patchOffer')
    cy.intercept({ method: 'GET', url: '/offers/*/stocks/*' }).as('getStocks')
    cy.intercept({ method: 'POST', url: '/stocks/bulk' }).as('postEventStocks')
    cy.intercept({ method: 'POST', url: '/stocks' }).as('postProductStock')
    cy.intercept({ method: 'PATCH', url: '/offers/publish' }).as('publishOffer')
    cy.intercept({ method: 'GET', url: '/offerers/names' }).as(
      'getOfferersNames'
    )
    cy.intercept({ method: 'GET', url: '/offers/categories' }).as(
      'getCategories'
    )
    cy.intercept({ method: 'GET', url: '/venues?offererId=*' }).as(
      'getVenuesForOfferer'
    )
    interceptSearch5Adresses()
  })

  after(() => {
    cy.wrap(Cypress.session.clearAllSavedSessions())
  })

  it('I should be able to create an individual offer (event)', () => {
    cy.wrap(Cypress.session.clearAllSavedSessions())
    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
      (response) => {
        logInAndGoToPage(response.body.user.email, '/offre/creation')
        venueName = response.body.venueName
      }
    )

    cy.stepLog({
      message: 'I want to create "Un évènement physique daté" offer',
    })
    cy.findByText('Au grand public').click()
    cy.findByText('Un évènement physique daté').click()
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
    cy.findByText('Étape suivante').click()

    cy.stepLog({ message: 'I fill in event details' })
    cy.findByLabelText(/Titre de l’offre/).type('Le Diner de Devs')
    cy.findByLabelText('Description').type(
      'Une PO invite des développeurs à dîner...'
    )
    cy.findByLabelText('Catégorie *').select('Spectacle vivant')
    cy.findByLabelText('Sous-catégorie *').select('Spectacle, représentation')
    cy.findByLabelText('Type de spectacle *').select('Théâtre')
    cy.findByLabelText('Sous-type *').select('Comédie')
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    // field image label is not seen
    cy.checkA11y(
      undefined,
      {
        ...DEFAULT_AXE_RULES,
        rules: {
          ...DEFAULT_AXE_RULES?.rules,
          'label-title-only': { enabled: false },
        },
      },
      cy.a11yLog
    )

    cy.stepLog({ message: 'I validate event details step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@getOffer', '@postDraftOffer'])

    cy.stepLog({ message: 'I fill in event useful informations' })
    cy.findByText('Retrait sur place (guichet, comptoir...)').click()
    cy.findByLabelText(/Email de contact communiqué aux bénéficiaires/).type(
      'passculture@example.com'
    )
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)

    cy.stepLog({ message: 'I validate event useful informations step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@getOffer', '@patchOffer'])

    // TODO: test video creation. This is only a workaround
    cy.url().should('contain', '/creation/media')
    cy.findByText('Enregistrer et continuer').click()
    cy.wait('@getOffer')

    cy.stepLog({ message: 'I fill in prices' })
    cy.findByLabelText('Intitulé du tarif').should('have.value', 'Tarif unique')
    cy.findByText('Ajouter un tarif').click()
    cy.findByText('Ajouter un tarif').click()

    cy.findAllByLabelText('Intitulé du tarif').eq(0).type('Carré Or')
    cy.findAllByLabelText(/Prix par personne/)
      .eq(0)
      .type('100')

    cy.findAllByLabelText('Intitulé du tarif').eq(1).type('Fosse Debout')
    cy.findAllByLabelText(/Prix par personne/)
      .eq(1)
      .type('10')

    cy.findAllByLabelText('Intitulé du tarif').eq(2).type('Fosse Sceptique')
    cy.findAllByRole('checkbox', { name: 'Gratuit' }).eq(2).click()

    cy.findByText('Accepter les réservations “Duo“').should('exist')
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)

    cy.stepLog({ message: 'I validate prices step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@patchOffer', '@getOffer', '@getStocks'], {
      responseTimeout: 60 * 1000 * 3,
    })

    cy.stepLog({ message: 'I fill in recurrence' })
    cy.findByRole('button', { name: 'Définir le calendrier' }).click()

    cy.findByText('Toutes les semaines').click()
    cy.findByLabelText('Vendredi').click()
    cy.findByLabelText('Samedi').click()
    cy.findByLabelText('Dimanche').click()
    cy.findByLabelText('Du *').type('2030-05-01')
    cy.findByLabelText('Au *').type('2030-09-30')
    cy.findByLabelText('Horaire 1 *').type('18:30')
    cy.findByText('Ajouter un créneau').click()
    cy.findByLabelText('Horaire 2 *').type('21:00')
    cy.findByText('Ajouter d’autres places et tarifs').click()
    cy.findByText('Ajouter d’autres places et tarifs').click()

    cy.findByTestId('wrapper-quantityPerPriceCategories.0').within(() => {
      // trouve la première liste déroulante avec le label:
      cy.findByLabelText('Tarif *').select('0,00\xa0€ - Fosse Sceptique')
    })

    cy.findAllByLabelText('Nombre de places').eq(0).type('100')

    cy.findByTestId('wrapper-quantityPerPriceCategories.1').within(() => {
      // trouve la euxième liste déroulante avec le label:
      cy.findByLabelText('Tarif *').select('10,00\xa0€ - Fosse Debout')
    })

    cy.findAllByLabelText('Nombre de places').eq(1).type('20')

    cy.findByTestId('wrapper-quantityPerPriceCategories.2').within(() => {
      // trouve la troisième liste déroulante avec le label:
      cy.findByLabelText('Tarif *').select('100,00\xa0€ - Carré Or')
    })

    // manque un data-testid ou un placeholder ou un label accessible
    cy.get('[name="bookingLimitDateInterval"]').type('3')

    cy.injectAxe(DEFAULT_AXE_CONFIG)
    // FIX ME: day selector has no visible label
    cy.checkA11y(
      undefined,
      {
        ...DEFAULT_AXE_RULES,
        rules: {
          ...DEFAULT_AXE_RULES?.rules,
          'label-title-only': { enabled: false },
        },
      },
      cy.a11yLog
    )
    cy.stepLog({ message: 'I validate recurrence step' })
    cy.findByText('Valider').click()
    cy.wait(['@postEventStocks', '@getStocks'])

    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
    cy.findByText('Enregistrer et continuer').click()
    cy.contains('Accepter les réservations "Duo" : Oui')

    cy.stepLog({ message: 'I publish my offer' })
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
    cy.findByText('Publier l’offre').click()
    cy.findByText('Plus tard').click()
    cy.wait(['@publishOffer', '@getOffer'], {
      requestTimeout: 60000 * 2,
      responseTimeout: 60000 * 2,
    })

    cy.stepLog({ message: 'I go to the offers list' })
    cy.findByText('Voir la liste des offres').click()
    cy.wait(['@getOffer', '@getCategories'], {
      requestTimeout: 60 * 1000 * 3,
      responseTimeout: 60 * 1000 * 3,
    })

    cy.stepLog({ message: 'my new offer should be displayed' })
    cy.url().should('contain', '/offres')
    cy.contains('Le Diner de Devs')
    cy.contains('396 dates')
  })

  it('I should be able to create an individual offer (thing)', () => {
    cy.visit('/offre/creation')
    const offerTitle = 'H2G2 Le Guide du voyageur galactique'
    const offerDesc =
      'Une quête pour obtenir la question ultime sur la vie, l’univers et tout le reste.'

    cy.stepLog({ message: 'I want to create "Un bien physique" offer' })
    cy.findByText('Au grand public').click()
    cy.findByText('Un bien physique').click()
    cy.findByText('Étape suivante').click()

    cy.stepLog({ message: 'I fill in details for physical offer' })
    cy.findByLabelText(/Titre de l’offre/).type(offerTitle)
    cy.findByLabelText('Description').type(offerDesc)

    // Random 13-digit number because we can't use the same EAN twice
    const ean = String(
      Math.floor(1000000000000 + Math.random() * 9000000000000)
    )
    cy.wrap(ean).as('ean')
    cy.findByLabelText('Catégorie *').select('Livre')
    cy.findByLabelText('Sous-catégorie *').select('Livre papier')
    cy.findByLabelText('Auteur').type('Douglas Adams')
    cy.findByLabelText('EAN-13 (European Article Numbering)').type(ean)
    /* TODO: this was moved to the media step
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

    cy.findByText('Importer').click()*/

    cy.stepLog({ message: 'the details of offer should be correct' })
    cy.findByLabelText(/Titre de l’offre/).should('have.value', offerTitle)
    cy.findByLabelText('Description').should('have.text', offerDesc)

    /* TODO: this was moved to the media step
    // With a 1.7x zoom, width=470 and height=705
    cy.findAllByTestId('image-preview').then(($img) => {
      cy.wrap($img)
        .should('be.visible')
        .should('have.prop', 'naturalWidth')
        .and('eq', 470)
      cy.wrap($img)
        .should('be.visible')
        .should('have.prop', 'naturalHeight')
        .and('eq', 705)
    })*/

    cy.stepLog({ message: 'I validate offer details step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@getOffer', '@postDraftOffer'])

    cy.stepLog({ message: 'I fill in useful informations for physical offer' })
    cy.findByLabelText('Informations de retrait').type(
      'Seuls les dauphins et les souris peuvent le lire.'
    )
    cy.findByText('Non accessible').click()
    cy.findByText('Psychique ou cognitif').click()
    cy.findByText('Moteur').click()
    cy.findByText('Auditif').click()

    cy.findByText('Être notifié par email des réservations').click()

    cy.stepLog({ message: 'I validate offer useful informations step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@getOffer', '@patchOffer'], {
      responseTimeout: 60 * 1000 * 2,
    })

    // TODO: test video creation. This is only a workaround
    cy.url().should('contain', '/creation/media')
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@getOffer', '@getStocks'], {
      responseTimeout: 60 * 1000 * 2,
    })

    cy.stepLog({ message: 'I fill in stocks' })
    cy.findByLabelText(/Prix/).type('42')
    cy.get('[data-testid="bookingLimitDatetime"').type('2042-05-03')
    cy.findByLabelText(/Quantité/).type(stock)

    cy.stepLog({ message: 'I validate stocks step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@patchOffer', '@postProductStock', '@getOffer'], {
      responseTimeout: 30 * 1000,
    })

    cy.stepLog({ message: 'I publish my offer' })
    cy.findByText('Publier l’offre').click()

    cy.wait(['@publishOffer', '@getOffer'], {
      requestTimeout: 60000 * 2,
      responseTimeout: 60000 * 2,
    })
    cy.stepLog({ message: 'I go to the offers list' })
    cy.findByText('Voir la liste des offres').click()
    cy.url().should('contain', '/offres')
    cy.wait(['@getOffer', '@getCategories'], {
      requestTimeout: 60 * 1000 * 3,
      responseTimeout: 60 * 1000 * 3,
    })

    cy.stepLog({ message: 'my new physical offer should be displayed' })
    const expectedNewResults = [
      ['', "Nom de l'offre", 'Lieu', 'Stocks', 'Statut', ''],
      ['', offerTitle, venueName, stock, 'publiée'],
      [],
    ]

    expectOffersOrBookingsAreFoundForNewTable(expectedNewResults)
    cy.get('@ean').then((ean) => {
      cy.contains(ean.toString())
    })
  })
})
