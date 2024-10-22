import { addDays, format } from 'date-fns'

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
    IGoToCollectivePage(login)

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

    expectOffersAreFound(expectedResults)
  })

  it('It should find collective bookings by establishments', () => {
    IGoToCollectivePage(login)

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
    expectOffersAreFound(expectedResults)
  })

  it('It should find collective bookings by booking number', () => {
    IGoToCollectivePage(login)

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
    expectOffersAreFound(expectedResults)
  })

  it('It should find collective bookings by date and by establishment', () => {
    IGoToCollectivePage(login)

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
    expectOffersAreFound(expectedResults)
  })
})

function expectOffersAreFound(expectedResults: Array<Array<string>>) {
  for (let rowLine = 0; rowLine < expectedResults.length - 1; rowLine++) {
    const offerLineArray = expectedResults[rowLine + 1]

    cy.findAllByTestId('offer-item-row')
      .eq(rowLine)
      .within(() => {
        cy.get('td').then(($elt) => {
          for (let column = 0; column < 5; column++) {
            cy.wrap($elt)
              .eq(column)
              .then((cellValue) => {
                if (cellValue.text().length && offerLineArray[column].length) {
                  return cy
                    .wrap(cellValue)
                    .should('contain.text', offerLineArray[column])
                } else {
                  return true
                }
              })
          }
        })
      })
  }
}

function IGoToCollectivePage(login: string) {
  const password = 'user@AZERTY123'

  cy.stepLog({ message: 'I am logged in' })
  cy.login({
    email: login,
    password: password,
    redirectUrl: '/',
  })
  cy.findAllByTestId('spinner').should('not.exist')

  cy.stepLog({ message: 'I open the "reservations/collectives" page' })
  cy.visit('/reservations/collectives')
}
