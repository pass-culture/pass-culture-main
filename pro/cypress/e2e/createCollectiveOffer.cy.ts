import { addDays, format } from 'date-fns'

import {
  DEFAULT_AXE_CONFIG,
  DEFAULT_AXE_RULES,
  MOCKED_BACK_ADDRESS_LABEL,
} from '../support/constants.ts'
import {
  expectOffersOrBookingsAreFound,
  interceptSearch5Adresses,
  logInAndGoToPage,
} from '../support/helpers.ts'

describe('Create collective offers', () => {
  let login: string
  let offerDraft: { name: string; venueName: string }
  const newOfferName = 'Ma nouvelle offre collective créée'
  const venueName = 'Mon Lieu 1'
  const venueFullAddress = '1 boulevard Poissonnière, 75002, Paris'
  const defaultDate = addDays(new Date(), 2)
  const defaultBookingLimitDate = addDays(new Date(), 1)

  const commonOfferData = {
    title: newOfferName,
    description: 'Bookable draft offer',
    email: 'example@passculture.app',
    date: defaultDate,
    bookingLimitDate: defaultBookingLimitDate,
    time: '18:30',
    participants: '10',
    price: '10',
    priceDescription: 'description',
    institution: 'COLLEGE 123',
  }

  beforeEach(() => {
    cy.visit('/')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_pro_user_with_collective_offers',
      (response) => {
        login = response.body.user.email
        offerDraft = response.body.offerDraft
      }
    )
    cy.intercept(
      'GET',
      'http://localhost:5001/collective/educational-domains',
      {
        body: [
          { id: 2, name: 'Danse', nationalPrograms: [] },
          { id: 3, name: 'Architecture', nationalPrograms: [] },
        ],
      }
    ).as('getDomains')

    cy.intercept({ method: 'GET', url: '/collective/offers*' }).as(
      'collectiveOffers'
    )
    cy.intercept({ method: 'GET', url: '/offerers/educational*' }).as(
      'educationalOfferers'
    )
    interceptSearch5Adresses()
  })

  const fillBasicOfferForm = () => {
    cy.findByText('Étape suivante').click()
    cy.wait('@getDomains')
    cy.findByLabelText(/Structure/).select(venueName)
    cy.findByLabelText('Domaines artistiques').click()
    cy.findByLabelText('Architecture').click()
    cy.findByText('Quel est le type de votre offre ?').click()
    cy.findByLabelText('Formats').click()
    cy.findByLabelText('Concert').click()
    cy.findByText('Quel est le type de votre offre ?').click()
  }

  const fillOfferDetails = (data = commonOfferData) => {
    cy.findByLabelText(/Titre de l’offre/).type(data.title)
    cy.findByLabelText(
      'Décrivez ici votre projet et son interêt pédagogique *'
    ).type(data.description)
    cy.findByText('Collège').click()
    cy.findByText('6e').click()
    cy.findAllByLabelText(/Email/).eq(0).type(data.email)
    cy.findByLabelText(/Email auquel envoyer les notifications/).type(
      data.email
    )
    cy.findByText('Enregistrer et continuer').click()
  }

  const fillDatesAndPrice = (data = commonOfferData) => {
    cy.findByLabelText('Date de début').type(format(data.date, 'yyyy-MM-dd'))
    cy.findByLabelText('Horaire').type(data.time)
    cy.findByLabelText('Nombre de participants').type(data.participants)
    cy.findByLabelText(/Prix total TTC/).type(data.price)
    cy.findByLabelText('Informations sur le prix').type(data.priceDescription)
    cy.findByLabelText('Date limite de réservation').type(
      format(data.bookingLimitDate, 'yyyy-MM-dd')
    )
    cy.findByText('Enregistrer et continuer').click()
  }

  const fillInstitution = (data = commonOfferData) => {
    cy.findByLabelText('Nom de l’établissement scolaire ou code UAI *').type(
      data.institution
    )
    cy.get('#list-institution').findByText(new RegExp(data.institution)).click()
    cy.findByText('Enregistrer et continuer').click()
  }

  const verifyAndPublishOffer = (data = commonOfferData) => {
    cy.findByText('Enregistrer et continuer').click()
    cy.findByText('Publier l’offre').click()
    cy.findByText('Voir mes offres').click()

    // Attendre que la page des offres soit chargée
    cy.wait('@collectiveOffers')

    // Rechercher l'offre
    // eslint-disable-next-line cypress/unsafe-to-chain-command
    cy.findByRole('searchbox', { name: /Nom de l’offre/ })
      .clear()
      .type(data.title)
    cy.findByText('Rechercher').click()

    // Attendre que les résultats soient chargés
    cy.wait('@collectiveOffers')

    // Vérifier les résultats
    const expectedResults = [
      [
        '',
        '',
        'Titre',
        'Date de l’évènement',
        'Lieu',
        'Établissement',
        'Statut',
      ],
      [
        '',
        '',
        data.title,
        `${format(data.date, 'dd/MM/yyyy')}`,
        venueName,
        data.institution,
        'publiée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  }

  it('Create collective bookable offers with a precise address (the venue address, selected by default)', () => {
    logInAndGoToPage(login, '/offre/creation')
    cy.findByText('À un groupe scolaire').click()
    fillBasicOfferForm()
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
    fillOfferDetails()
    cy.findByRole('heading', {
      name: 'Indiquez le prix et la date de votre offre',
    })
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    // label of image is not seen
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
    fillDatesAndPrice()
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
    fillInstitution()
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
    cy.contains(`Adresse : ${venueFullAddress}`)
    verifyAndPublishOffer()
  })

  it('Create collective bookable offers with a precise address (another address)', () => {
    logInAndGoToPage(login, '/offre/creation')
    cy.findByText('À un groupe scolaire').click()
    fillBasicOfferForm()
    cy.findByLabelText('Autre adresse').click()
    cy.findByLabelText(/Adresse postale/).type(MOCKED_BACK_ADDRESS_LABEL)
    cy.wait('@search5Address').its('response.statusCode').should('eq', 200)
    cy.findByTestId('list').contains(MOCKED_BACK_ADDRESS_LABEL).click()
    fillOfferDetails()
    fillDatesAndPrice()
    fillInstitution()
    cy.contains('Adresse : 3 RUE DE VALOIS, 75008, Paris')
    verifyAndPublishOffer()
  })

  it('Create collective bookable offers with a precise address (another address - manual entry)', () => {
    logInAndGoToPage(login, '/offre/creation')
    cy.findByText('À un groupe scolaire').click()
    fillBasicOfferForm()
    cy.findByLabelText('Autre adresse').click()
    cy.findByLabelText('Intitulé de la localisation').type(
      'Libellé de mon adresse custom'
    )
    cy.findByText('Vous ne trouvez pas votre adresse ?').click()
    cy.findAllByLabelText(/Adresse postale/)
      .last()
      .type('10 Rue du test')
    cy.findAllByLabelText(/Code postal/).type('75002')
    cy.findAllByLabelText(/Ville/).type('Paris')
    // eslint-disable-next-line cypress/unsafe-to-chain-command
    cy.findAllByLabelText(/Coordonnées GPS/)
      .type('48.853320, 2.348979')
      .blur()
    cy.findByText('Vérifiez la localisation en cliquant ici').should(
      'be.visible'
    )
    fillOfferDetails()
    fillDatesAndPrice()
    fillInstitution()
    cy.contains('Intitulé : Libellé de mon adresse custom')
    cy.contains('Adresse : 10 Rue du test, 75002, Paris')
    verifyAndPublishOffer()
  })

  it('Create collective bookable offers with school location', () => {
    logInAndGoToPage(login, '/offre/creation')
    cy.findByText('À un groupe scolaire').click()
    fillBasicOfferForm()
    cy.findByLabelText('En établissement scolaire').click()
    fillOfferDetails()

    fillDatesAndPrice()
    fillInstitution()
    cy.contains('Dans l’établissement scolaire')
    cy.contains('Zone de mobilité : Paris (75) - Hauts-de-Seine (92)')
    verifyAndPublishOffer()
  })

  it('Create collective bookable offers with to be defined location', () => {
    logInAndGoToPage(login, '/offre/creation')
    cy.findByText('À un groupe scolaire').click()
    fillBasicOfferForm()
    cy.findByLabelText('À déterminer avec l’enseignant').click()
    cy.findByLabelText('Commentaire').type('Test commentaire')
    fillOfferDetails()
    fillDatesAndPrice()
    fillInstitution()
    cy.contains('À déterminer avec l’enseignant')
    cy.contains('Commentaire : Test commentaire')
    cy.contains('Zone de mobilité : Paris (75) - Hauts-de-Seine (92)')
    verifyAndPublishOffer()
  })

  it('Create collective offer template and use it in duplication page', () => {
    logInAndGoToPage(login, '/offre/creation')
    cy.findByText('À un groupe scolaire').click()
    cy.findByText('Une offre vitrine').click()
    cy.findByText('Étape suivante').click()
    fillBasicOfferForm()
    cy.findByLabelText(/Titre de l’offre/).type(commonOfferData.title)
    cy.findByLabelText(
      'Décrivez ici votre projet et son interêt pédagogique *'
    ).type(commonOfferData.description)
    cy.findByText('Collège').click()
    cy.findByText('6e').click()
    cy.findByLabelText(/Email auquel envoyer les notifications/).type(
      commonOfferData.email
    )
    cy.findByLabelText('Via un formulaire').click()
    cy.findByText('Enregistrer et continuer').click()
    cy.contains('Intitulé : Mon Lieu 1')
    cy.contains(`Adresse : ${venueFullAddress}`)
    cy.findByText('Enregistrer et continuer').click()
    cy.findByText('Publier l’offre').click()
    cy.findByText('Voir mes offres').click()

    // Attendre que la page des offres soit chargée
    cy.wait('@collectiveOffers')

    // Rechercher l'offre
    // eslint-disable-next-line cypress/unsafe-to-chain-command
    cy.findByRole('searchbox', { name: /Nom de l’offre/ })
      .clear()
      .type(commonOfferData.title)
    cy.findByText('Rechercher').click()

    // Attendre que les résultats soient chargés
    cy.wait('@collectiveOffers')

    // Vérifier les résultats
    const expectedResults = [
      [
        '',
        '',
        'Titre',
        'Date de l’évènement',
        'Lieu',
        'Établissement',
        'Statut',
      ],
      [
        '',
        '',
        commonOfferData.title,
        'Toute l’année scolaire',
        venueName,
        'Tous les établissements',
        'publiée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)

    cy.visit('/offre/creation')
    cy.findByText('À un groupe scolaire').click()
    cy.findByText('Dupliquer les informations d’une offre vitrine').click()
    cy.findByText('Étape suivante').click()
    cy.intercept({
      method: 'GET',
      url: '/collective/offers?offererId=1&status=PUBLISHED&status=HIDDEN&status=ENDED&collectiveOfferType=template',
    }).as('duplicateOffers')
    cy.wait('@duplicateOffers')
    cy.findByText(newOfferName).click()
    // eslint-disable-next-line cypress/unsafe-to-chain-command
    cy.findByLabelText(/Titre de l’offre/)
      .clear()
      .type('Offre dupliquée OA')
    cy.findAllByLabelText(/Email/).eq(0).type(commonOfferData.email)
    cy.findByText('Enregistrer et continuer').click()
    fillDatesAndPrice()
    fillInstitution()
    cy.contains('Intitulé : Mon Lieu 1')
    cy.contains(`Adresse : ${venueFullAddress}`)
    verifyAndPublishOffer({ ...commonOfferData, title: 'Offre dupliquée OA' })
  })

  it('Create collective bookable offers with a precise address (the venue address, selected by default) and update location', () => {
    logInAndGoToPage(login, '/offre/creation')
    cy.findByText('À un groupe scolaire').click()
    fillBasicOfferForm()
    fillOfferDetails()
    fillDatesAndPrice()
    fillInstitution()
    cy.contains(`Adresse : ${venueFullAddress}`)
    verifyAndPublishOffer()
    cy.findAllByTestId('offer-item-row')
      .eq(0)
      .within(() => cy.findByRole('link', { name: newOfferName }).click())
    cy.findAllByText('Modifier').eq(0).click()
    cy.findByLabelText('Autre adresse').click()
    // eslint-disable-next-line cypress/unsafe-to-chain-command
    cy.findByLabelText('Intitulé de la localisation')
      .clear()
      .type('Libellé de mon adresse custom')
    cy.findByLabelText(/Adresse postale/).type(MOCKED_BACK_ADDRESS_LABEL)
    cy.wait('@search5Address').its('response.statusCode').should('eq', 200)
    cy.findByTestId('list').contains(MOCKED_BACK_ADDRESS_LABEL).click()
    cy.findByText('Enregistrer et continuer').click()
    cy.contains('Libellé de mon adresse custom')
    cy.contains('3 RUE DE VALOIS, 75008, Paris')
  })

  it('Create an offer with draft status and publish it', () => {
    logInAndGoToPage(login, '/offre/creation')
    cy.findByText('À un groupe scolaire').click()
    fillBasicOfferForm()
    cy.findByLabelText('Autre adresse').click()
    cy.findByLabelText(/Adresse postale/).type(MOCKED_BACK_ADDRESS_LABEL)
    cy.wait('@search5Address').its('response.statusCode').should('eq', 200)
    cy.findByTestId('list').contains(MOCKED_BACK_ADDRESS_LABEL).click()
    fillOfferDetails()
    fillDatesAndPrice()
    fillInstitution()

    cy.findByRole('heading', { name: 'Détails de l’offre' }).should('exist')
    cy.findByText('Enregistrer et continuer').click()
    cy.findByText('Sauvegarder le brouillon et quitter').click()

    cy.findByText('Brouillon sauvegardé dans la liste des offres')

    cy.stepLog({ message: 'I want to see my offer in draft status' })

    cy.wait('@collectiveOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'I open the filters' })
    cy.findByText('Filtrer').click()

    cy.findByRole('button', { name: 'Statut' }).click()
    cy.findByTestId('panel-scrollable').scrollTo('bottom')
    cy.findByText('Brouillon').click()

    // We click outside the filter to close it
    cy.findByRole('heading', { name: 'Offres collectives' }).click()
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffers')

    const draftResults = [
      [
        '',
        '',
        'Titre',
        'Date de l’évènement',
        'Lieu',
        'Établissement',
        'Statut',
      ],
      [
        '',
        '',
        commonOfferData.title,
        `${format(commonOfferData.date, 'dd/MM/yyyy')}`,
        venueName,
        commonOfferData.institution,
        'brouillon',
      ],
      [
        '',
        '',
        offerDraft.name,
        '-',
        offerDraft.venueName,
        'DE LA TOUR',
        'brouillon',
      ],
    ]

    expectOffersOrBookingsAreFound(draftResults)

    cy.stepLog({ message: 'I want to change my offer to published status' })
    cy.findAllByTestId('offer-item-row')
      .eq(0)
      .within(() => cy.findByRole('link', { name: newOfferName }).click())

    cy.wait('@educationalOfferers')

    cy.findByRole('link', { name: '5 Aperçu' }).click()
    cy.findByText('Publier l’offre').click()
    cy.findByText('Voir mes offres').click()

    cy.stepLog({ message: 'I want to see my offer in published status' })

    cy.url().should('contain', '/offres/collectives')

    cy.findByText('Réinitialiser les filtres').click()
    cy.findByRole('searchbox', { name: /Nom de l’offre/ }).type(newOfferName)
    cy.findByText('Rechercher').click()

    // Attendre que les résultats soient chargés
    cy.wait('@collectiveOffers')

    const expectedResults = [
      [
        '',
        '',
        'Titre',
        'Date de l’évènement',
        'Lieu',
        'Établissement',
        'Statut',
      ],
      [
        '',
        '',
        commonOfferData.title,
        `${format(commonOfferData.date, 'dd/MM/yyyy')}`,
        venueName,
        commonOfferData.institution,
        'publiée',
      ],
    ]
    expectOffersOrBookingsAreFound(expectedResults)
  })
})
