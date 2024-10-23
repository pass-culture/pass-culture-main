import { addDays, format } from 'date-fns'

import {
  expectOffersOrBookingsAreFound,
  logAndGoToPage,
} from '../support/helpers.ts'

describe('Search for collective bookings', () => {
  let login: string

  beforeEach(() => {
    cy.visit('/connexion')
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_pro_user_with_collective_bookings',
    }).then((response) => {
      login = response.body.user.email
    })
  })

  it('It should find collective bookings by offers', () => {
    logAndGoToPage(login, '/reservations/collectives')

    cy.stepLog({ message: 'I display bookings' })
    cy.findByText('Afficher').click()
    cy.findByTestId('spinner').should('not.exist')

    cy.stepLog({ message: 'I search for "Offre" with text "Mon offre"' })
    cy.findByTestId('select-omnisearch-criteria').select('Offre')
    cy.findByTestId('omnisearch-filter-input-text').type('Mon offre')

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      [
        'Réservation',
        "Nom de l'offre",
        'Établissement',
        'Places et prix',
        'Statut',
      ],
      ['1', 'Mon offre', 'COLLEGE DE LA TOUR', '25 places100 €', 'confirmée'],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it('It should find collective bookings by establishments', () => {
    logAndGoToPage(login, '/reservations/collectives')

    cy.stepLog({ message: 'I display bookings' })
    cy.findByText('Afficher').click()
    cy.findByTestId('spinner').should('not.exist')

    cy.stepLog({
      message: 'I search for "Établissement" with text "Victor Hugo"',
    })
    cy.findByTestId('select-omnisearch-criteria').select('Établissement')
    cy.findByTestId('omnisearch-filter-input-text').type('Victor Hugo')

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      [
        'Réservation',
        "Nom de l'offre",
        'Établissement',
        'Places et prix',
        'Statut',
      ],
      [
        '4',
        'Mon autre offre',
        'COLLEGE Victor Hugo',
        '25 places100 €',
        'confirmée',
      ],
    ]
    expectOffersOrBookingsAreFound(expectedResults)
  })

  it('It should find collective bookings by booking number', () => {
    logAndGoToPage(login, '/reservations/collectives')

    cy.stepLog({ message: 'I display bookings' })
    cy.findByText('Afficher').click()
    cy.findByTestId('spinner').should('not.exist')

    cy.stepLog({
      message: 'I search for "Numéro de réservation" with text "2"',
    })
    cy.findByTestId('select-omnisearch-criteria').select(
      'Numéro de réservation'
    )
    cy.findByTestId('omnisearch-filter-input-text').type('2')

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      [
        'Réservation',
        "Nom de l'offre",
        'Établissement',
        'Places et prix',
        'Statut',
      ],
      [
        '2',
        'Encore une autre offre',
        'COLLEGE Autre collège',
        '25 places100 €',
        'confirmée',
      ],
    ]
    expectOffersOrBookingsAreFound(expectedResults)
  })

  it('It should find collective bookings by date and by establishment', () => {
    logAndGoToPage(login, '/reservations/collectives')

    const dateSearch = format(addDays(new Date(), 10), 'yyyy-MM-dd')
    cy.findByLabelText('Date de l’évènement').type(dateSearch)

    cy.stepLog({ message: 'I display bookings' })
    cy.findByText('Afficher').click()
    cy.findByTestId('spinner').should('not.exist')

    cy.stepLog({
      message: 'I search for "Établissement" with text "COLLEGE DE LA TOUR"',
    })
    cy.findByTestId('select-omnisearch-criteria').select('Établissement')
    cy.findByTestId('omnisearch-filter-input-text').type('COLLEGE DE LA TOUR')

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      [
        'Réservation',
        "Nom de l'offre",
        'Établissement',
        'Places et prix',
        'Statut',
      ],
      ['1', 'Mon offre', 'COLLEGE DE LA TOUR', '25 places100 €', 'confirmée'],
    ]
    expectOffersOrBookingsAreFound(expectedResults)
  })
})
