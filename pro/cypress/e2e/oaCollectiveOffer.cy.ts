import { addDays, format } from 'date-fns'

import {
  expectOffersOrBookingsAreFound,
  logInAndGoToPage,
} from '../support/helpers.ts'

describe('Create collective offers with OA', () => {
  let login: string
  const newOfferName = 'Ma nouvelle offre collective créée'
  const venueName = 'Mon Lieu 1'
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
    cy.setFeatureFlags([
      { name: 'WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE', isActive: true },
    ])
  })

  const fillBasicOfferForm = () => {
    cy.findByText('Étape suivante').click()
    cy.wait('@getDomains')
    cy.findByLabelText('Structure *').select(venueName)
    cy.findByLabelText('Domaines artistiques').click()
    cy.findByLabelText('Architecture').click()
    cy.findByText('Quel est le type de votre offre ?').click()
    cy.findByLabelText('Formats').click()
    cy.findByLabelText('Concert').click()
    cy.findByText('Quel est le type de votre offre ?').click()
  }

  const fillOfferDetails = (data = commonOfferData) => {
    cy.findByLabelText('Titre de l’offre *').type(data.title)
    cy.findByLabelText(
      'Décrivez ici votre projet et son interêt pédagogique *'
    ).type(data.description)
    cy.findByText('Collège').click()
    cy.findByText('6e').click()
    cy.findByLabelText('Email *').type(data.email)
    cy.findByLabelText('Email auquel envoyer les notifications *').type(
      data.email
    )
    cy.findByText('Enregistrer et continuer').click()
  }

  const fillDatesAndPrice = (data = commonOfferData) => {
    cy.findByLabelText('Date de début').type(format(data.date, 'yyyy-MM-dd'))
    cy.findByLabelText('Horaire').type(data.time)
    cy.findByLabelText('Nombre de participants').type(data.participants)
    cy.findByLabelText('Prix total TTC').type(data.price)
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
        '',
        data.title,
        `${format(data.date, 'dd/MM/yyyy')}18h30`,
        venueName,
        data.institution,
        'publiée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  }

  it('Create collective bookable offers with OA (Precise address - Venue)', () => {
    logInAndGoToPage(login, '/offre/creation')
    cy.findByText('À un groupe scolaire').click()
    fillBasicOfferForm()
    fillOfferDetails()
    fillDatesAndPrice()
    fillInstitution()
    cy.contains('Adresse : 1 boulevard Poissonnière, 75002, Paris')
    verifyAndPublishOffer()
  })

  it('Create collective bookable offers with OA (Precise address - Other address)', () => {
    logInAndGoToPage(login, '/offre/creation')
    cy.findByText('À un groupe scolaire').click()
    fillBasicOfferForm()
    cy.findByLabelText('Autre adresse').click()
    cy.findByLabelText('Adresse postale *').type('10 Rue')
    cy.get('[data-testid="list"] li').first().click()
    fillOfferDetails()
    fillDatesAndPrice()
    fillInstitution()
    cy.contains('Adresse : 10 Rue, 53210, Argentré')
    verifyAndPublishOffer()
  })

  it('Create collective bookable offers with OA (Precise address - Other address - Manual Address)', () => {
    logInAndGoToPage(login, '/offre/creation')
    cy.findByText('À un groupe scolaire').click()
    fillBasicOfferForm()
    cy.findByLabelText('Autre adresse').click()
    cy.findByLabelText('Intitulé de la localisation').type(
      'Libellé de mon adresse custom'
    )
    cy.findByText('Vous ne trouvez pas votre adresse ?').click()
    cy.findAllByLabelText('Adresse postale *').last().type('10 Rue du test')
    cy.findAllByLabelText('Code postal *').type('75002')
    cy.findAllByLabelText('Ville *').type('Paris')
    // eslint-disable-next-line cypress/unsafe-to-chain-command
    cy.findAllByLabelText('Coordonnées GPS *')
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

  it('Create collective bookable offers with OA (In school)', () => {
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

  it('Create collective bookable offers with OA (Other)', () => {
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

  it('Create collective offer template and used it in duplication page', () => {
    logInAndGoToPage(login, '/offre/creation')
    cy.findByText('À un groupe scolaire').click()
    cy.findByText('Une offre vitrine').click()
    cy.findByText('Étape suivante').click()
    fillBasicOfferForm()
    cy.findByLabelText('Titre de l’offre *').type(commonOfferData.title)
    cy.findByLabelText(
      'Décrivez ici votre projet et son interêt pédagogique *'
    ).type(commonOfferData.description)
    cy.findByText('Collège').click()
    cy.findByText('6e').click()
    cy.findByLabelText('Email auquel envoyer les notifications *').type(
      commonOfferData.email
    )
    cy.findByLabelText('Via un formulaire').click()
    cy.findByText('Enregistrer et continuer').click()
    cy.contains('Intitulé : Mon Lieu 1')
    cy.contains('Adresse : 1 boulevard Poissonnière, 75002, Paris')
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
    cy.findByText('Étape suivante').click()
    // eslint-disable-next-line cypress/unsafe-to-chain-command
    cy.findByLabelText('Titre de l’offre *').clear().type('Offre dupliquée OA')
    cy.findByLabelText('Email *').type(commonOfferData.email)
    cy.findByText('Enregistrer et continuer').click()
    fillDatesAndPrice()
    fillInstitution()
    cy.contains('Intitulé : Mon Lieu 1')
    cy.contains('Adresse : 1 boulevard Poissonnière, 75002, Paris')
    cy.findByText('Enregistrer et continuer').click()
    verifyAndPublishOffer({ ...commonOfferData, title: 'Offre dupliquée OA' })
  })

  it('Create collective bookable offers with OA (Precise address - Venue) and update localisation', () => {
    logInAndGoToPage(login, '/offre/creation')
    cy.findByText('À un groupe scolaire').click()
    fillBasicOfferForm()
    fillOfferDetails()
    fillDatesAndPrice()
    fillInstitution()
    cy.contains('Adresse : 1 boulevard Poissonnière, 75002, Paris')
    verifyAndPublishOffer()
    cy.findAllByTestId('offer-item-row')
      .eq(0)
      .within(() => cy.findByRole('link', { name: newOfferName }).click())
    cy.findAllByText('Modifier').eq(0).click()
    cy.findByLabelText('Autre adresse').click()
    // eslint-disable-next-line cypress/unsafe-to-chain-command
    cy.findByLabelText('Intitulé de la localisation').clear().type(
      'Libellé de mon adresse custom'
    )
    cy.findByLabelText('Adresse postale *').type('10 Rue')
    cy.get('[data-testid="list"] li').first().click()
      cy.findByText('Enregistrer et continuer').click()
      cy.contains('Intitulé : Libellé de mon adresse custom')
      cy.contains('Adresse : 10 Rue, 53210, Argentré')
  })
})
