import { addDays, format } from 'date-fns'

import { DEFAULT_AXE_CONFIG, DEFAULT_AXE_RULES } from '../support/constants.ts'
import {
  expectOffersOrBookingsAreFound,
  sessionLogInAndGoToPage,
} from '../support/helpers.ts'

describe('Search individual offers', () => {
  let login: string
  let venueName0: string
  let venueName: string
  let venueFullAddress0: string
  let venueFullAddress: string
  let offerName0: string
  let offerName1: string
  let offerName2: string
  let offerName3: string
  let offerName4: string
  let offerName5: string
  let offerName6: string
  let offerName7: string

  before(() => {
    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_pro_user_with_individual_offers',
      (response) => {
        login = response.body.user.email
        venueName0 = response.body.venue0.name
        venueName = response.body.venue.name
        venueFullAddress0 = response.body.venue0.fullAddress
        venueFullAddress = response.body.venue.fullAddress
        offerName0 = response.body.offer0.name
        offerName1 = response.body.offer1.name
        offerName2 = response.body.offer2.name
        offerName3 = response.body.offer3.name
        offerName4 = response.body.offer4.name
        offerName5 = response.body.offer5.name
        offerName6 = response.body.offer6.name
        offerName7 = response.body.offer7.name
      }
    )
  })

  beforeEach(() => {
    sessionLogInAndGoToPage('Session search individual', login, '/offres')
    cy.intercept({
      method: 'GET',
      url: '/offers?**',
    }).as('searchOffers')
  })

  it('I should be able to search with a name and see expected results', () => {
    cy.stepLog({ message: 'I search with the text "Une super offre"' })

    cy.findByRole('searchbox', { name: /Nom de l’offre/ }).type(offerName1)
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      ['', 'Titre', 'Localisation', 'Stocks', 'Status'],
      [
        '',
        offerName1,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it('I should be able to search with a EAN and see expected results', () => {
    const ean = '1234567891234'

    cy.stepLog({ message: `I search with the text:${ean}` })
    cy.findByRole('searchbox', { name: /Nom de l’offre/ }).type(ean)

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      ['', 'Titre', 'Localisation', 'Stocks', 'Status'],
      [
        '',
        offerName2 + ean,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it('I should be able to search with "Catégorie" filter and see expected results', () => {
    cy.stepLog({ message: 'I open the filters' })
    cy.findByText('Filtrer').click()

    cy.stepLog({ message: 'I select "Instrument de musique" in "Catégorie"' })

    cy.findByRole('combobox', { name: /Catégorie/ })
      .select('Instrument de musique')
      .should('have.value', 'INSTRUMENT')

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      ['', 'Titre', 'Localisation', 'Stocks', 'Status'],
      [
        '',
        offerName3,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it('I should be able to search by offer status and see expected results', () => {
    cy.stepLog({ message: 'I open the filters' })
    cy.findByText('Filtrer').click()

    cy.stepLog({ message: 'I select "Publiée" in offer status' })

    cy.findAllByRole('combobox', { name: 'Statut' })
      .select('Publiée')
      .should('have.value', 'ACTIVE')

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'These 6 results should be displayed' })
    const expectedResults = [
      ['', 'Titre', 'Localisation', 'Stocks', 'Status'],
      [
        '',
        offerName6,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName5,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName4,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName3,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName2,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName1,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it('I should be able to search by date and see expected results', () => {
    cy.stepLog({ message: 'I open the filters' })
    cy.findByText('Filtrer').click()

    cy.stepLog({ message: 'I select a date in one month' })
    const dateSearch = format(addDays(new Date(), 30), 'yyyy-MM-dd')
    cy.findByLabelText('Début de la période').type(dateSearch)
    cy.findByLabelText('Fin de la période').type(dateSearch)

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      ['', 'Titre', 'Localisation', 'Stocks', 'Status'],
      [
        '',
        offerName4,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it('I should be able to search by venue and see expected results', () => {
    cy.stepLog({ message: 'I search with the text "Livre"' })
    cy.stepLog({ message: 'I open the filters' })
    cy.findByText('Filtrer').click()
    cy.findAllByRole('combobox', { name: 'Localisation' }).select(1)
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'These 7 results should be displayed' })
    const expectedResults2 = [
      ['', 'Titre', 'Localisation', 'Stocks', 'Status'],
      ['', offerName7, `${venueName} - ${venueFullAddress}`, '0', 'épuisée'],
      [
        '',
        offerName6,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName5,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName4,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName3,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName2,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName1,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults2)
  })

  it('I should be able to search combining several filters and see expected results', () => {
    cy.stepLog({ message: 'I search with the text "Livre"' })
    cy.findByRole('searchbox', { name: /Nom de l’offre/ }).type('incroyable')

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'I open the filters' })
    cy.findByText('Filtrer').click()

    cy.stepLog({ message: 'I select "Livre" in "Catégorie"' })
    cy.findByLabelText('Catégorie').select('Livre')

    cy.stepLog({ message: 'I select "Mon lieu" in "Localisation"' })
    cy.findByLabelText('Localisation').select(
      `${venueName} - ${venueFullAddress}`
    )

    cy.stepLog({ message: 'I select "Publiée" in offer status' })
    cy.findAllByRole('combobox', { name: 'Statut' }).select('Publiée')

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'These 2 results should be displayed' })
    const expectedResults = [
      ['', 'Titre', 'Localisation', 'Stocks', 'Status'],
      [
        '',
        offerName6,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName5,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)

    cy.stepLog({ message: 'I reset all filters' })
    cy.findByText('Réinitialiser les filtres').click()

    cy.stepLog({ message: 'All filters are empty' })
    cy.findByRole('searchbox', { name: /Nom de l’offre/ }).should('be.empty')
    cy.findAllByRole('combobox', { name: 'Localisation' })
      .invoke('val')
      .should('eq', 'all')

    cy.findByRole('combobox', { name: 'Catégorie' })
      .invoke('val')
      .should('eq', 'all')

    cy.findByRole('combobox', { name: 'Mode de création' })
      .invoke('val')
      .should('eq', 'all')

    cy.findAllByRole('combobox', { name: 'Statut' })
      .invoke('val')
      .should('eq', 'all')

    cy.findByLabelText('Début de la période').invoke('val').should('be.empty')
    cy.findByLabelText('Fin de la période').invoke('val').should('be.empty')

    cy.stepLog({ message: 'I reset the name search' })
    cy.findByLabelText(/Nom de l’offre/).clear()

    cy.stepLog({ message: 'I make a new search' })
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'These 7 results should be displayed' })
    const expectedResults2 = [
      ['', 'Titre', 'Localisation', 'Stocks', 'Status'],
      ['', offerName7, `${venueName} - ${venueFullAddress}`, '0', 'épuisée'],
      [
        '',
        offerName6,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName5,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName4,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName3,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName2,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName1,
        `${venueName} - ${venueFullAddress}`,
        '1 000',
        'publiée',
      ],
      ['', offerName0, `${venueName0} - ${venueFullAddress0}`, '0', 'épuisée'],
    ]

    expectOffersOrBookingsAreFound(expectedResults2)
  })
})
