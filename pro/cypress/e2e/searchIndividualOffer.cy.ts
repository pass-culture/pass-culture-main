import { addDays, format } from 'date-fns'

import {
  expectOffersOrBookingsAreFoundForNewTable,
  logInAndGoToPage
} from '../support/helpers.ts'

describe('Search individual offers', () => {
  let venueName: string
  let venueFullAddress: string
  let offerName1: string
  let offerName2: string
  let offerName3: string
  let offerName4: string
  let offerName5: string
  let offerName6: string
  let offerName7: string

  beforeEach(() => {
    cy.wrap(Cypress.session.clearAllSavedSessions())
    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_pro_user_with_individual_offers',
      (response) => {
        logInAndGoToPage(response.body.user.email, '/offres')
        venueName = response.body.venue.name
        venueFullAddress = response.body.venue.fullAddress
        offerName1 = response.body.offer1.name
        offerName2 = response.body.offer2.name
        offerName3 = response.body.offer3.name
        offerName4 = response.body.offer4.name
        offerName5 = response.body.offer5.name
        offerName6 = response.body.offer6.name
        offerName7 = response.body.offer7.name
      }
    )
    cy.intercept({
      method: 'GET',
      url: '/offers?**',
    }).as('searchOffers')
  })

  it('I should be able to search with a name and see expected results', () => {
    cy.stepLog({ message: 'I search with the text "Une super offre"' })
    cy.findByRole('searchbox', { name: /Nom de l’offre/ }).type(offerName1)

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

    expectOffersOrBookingsAreFoundForNewTable(expectedResults)
  })

  it('I should be able to search with a EAN and see expected results', () => {
    const ean = '1234567891234'

    cy.stepLog({ message: 'I search with the text:' + ean })
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

    expectOffersOrBookingsAreFoundForNewTable(expectedResults)
  })

  it('I should be able to search with "Catégorie" filter and see expected results', () => {
    cy.stepLog({ message: 'I open the filters' })
    cy.findByText('Filtrer').click()

    cy.stepLog({ message: 'I select "Instrument de musique" in "Catégorie"' })

    cy.findByTestId('wrapper-categorie').within(() => {
      cy.findByLabelText('Catégorie').select('Instrument de musique')
      cy.get('#categorie').should('have.value', 'INSTRUMENT')
    })

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

    expectOffersOrBookingsAreFoundForNewTable(expectedResults)
  })

  it('I should be able to search by offer status and see expected results', () => {
    cy.stepLog({ message: 'I open the filters' })
    cy.findByText('Filtrer').click()

    cy.stepLog({ message: 'I select "Publiée" in offer status' })

    cy.findByTestId('wrapper-status').within(() => {
      cy.findByLabelText('Statut').select('Publiée')
      cy.get('#status').should('have.value', 'ACTIVE')
    })

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

    expectOffersOrBookingsAreFoundForNewTable(expectedResults)
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

    expectOffersOrBookingsAreFoundForNewTable(expectedResults)
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
    cy.findByTestId('wrapper-status').within(() => {
      cy.get('select').select('Publiée')
    })

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

    expectOffersOrBookingsAreFoundForNewTable(expectedResults)

    cy.stepLog({ message: 'I reset all filters' })
    cy.findByText('Réinitialiser les filtres').click()

    cy.stepLog({ message: 'All filters are empty' })
    cy.findByRole('searchbox', { name: /Nom de l’offre/ }).should('be.empty')
    cy.findByTestId('wrapper-address').within(() => {
      cy.get('select').invoke('val').should('eq', 'all')
    })
    cy.findByTestId('wrapper-categorie').within(() => {
      cy.get('select').invoke('val').should('eq', 'all')
    })
    cy.findByTestId('wrapper-creationMode').within(() => {
      cy.get('select').invoke('val').should('eq', 'all')
    })
    cy.findByTestId('wrapper-status').within(() => {
      cy.get('select').invoke('val').should('eq', 'all')
    })
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
      [
        '',
        offerName7,
        `${venueName} - ${venueFullAddress}`,
        '0',
        'épuisée',
      ],
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

    expectOffersOrBookingsAreFoundForNewTable(expectedResults2)
  })
})
