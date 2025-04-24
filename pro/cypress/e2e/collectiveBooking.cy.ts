import { addDays, format } from 'date-fns'

import {
  expectOffersOrBookingsAreFound,
  logInAndGoToPage,
} from '../support/helpers.ts'

describe('Search for collective bookings', { testIsolation: false }, () => {
  before(() => {
    cy.wrap(Cypress.session.clearAllSavedSessions())
  })

  it('I should be able to find collective bookings by offers', () => {
    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_pro_user_with_collective_bookings',
      (response) => {
        logInAndGoToPage(response.body.user.email, '/reservations/collectives')
      }
    )

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

  it('I should be able to find collective bookings by establishments', () => {
    cy.visit('/reservations/collectives')
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

  it('I should be able to find collective bookings by booking number', () => {
    cy.visit('/reservations/collectives')
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

  it('I should be able to find collective bookings by date and by establishment', () => {
    cy.visit('/reservations/collectives')
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
