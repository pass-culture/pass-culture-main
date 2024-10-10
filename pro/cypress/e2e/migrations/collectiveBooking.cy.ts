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

describe('Search for collective bookings', () => {
  const login = 'retention_structures@example.com'
  const password = 'user@AZERTY123'

  beforeEach(() => {
    cy.visit('/connexion')
    // cy.request({
    //   method: 'GET',
    //   url: 'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
    // }).then((response) => {
    //   login = response.body.user.email
    // })
    // I am logged in with account 1

    cy.stepLog({ message: 'I am logged in' })
    cy.login({
      email: login,
      password: password,
      redirectUrl: '/',
    })

    cy.stepLog({ message: 'I select offerer "eac_2_lieu [BON EAC]"' })
    cy.findByTestId('offerer-select').click()
    cy.findByText(/Changer de structure/).click()
    cy.findByTestId('offerers-selection-menu')
      .findByText('eac_2_lieu [BON EAC]')
      .click()
    cy.findByTestId('header-dropdown-menu-div').should('not.exist')
    cy.findAllByTestId('spinner').should('not.exist')

    cy.stepLog({ message: 'I open the "reservations/collectives" page' })
    cy.visit('/reservations/collectives')
  })

  it('It should find collective bookings by offers', () => {
    cy.stepLog({ message: 'I display offers' })
    cy.findByText('Afficher').click()
    cy.findByTestId('spinner').should('not.exist')

    cy.stepLog({ message: 'I search for "Offre" with text "offer 39"' })
    cy.findByTestId('select-omnisearch-criteria').select('Offre')
    cy.findByTestId('omnisearch-filter-input-text').type('offer 39')

    cy.stepLog({ message: 'these 1 results should be displayed' })
    const expectedResults = [
      [
        'Réservation',
        "Nom de l'offre",
        'Établissement',
        'Places et prix',
        'Statut',
      ],
      [
        '80',
        'offer',
        'ECOLE ELEMENTAIRE PUBLIQUE FRANCOIS MOISSON',
        '25 places100 €',
        'annulée',
      ],
    ]

    expectOffersAreFound(expectedResults)
  })

  it('It should find collective bookings by establishments', () => {
    cy.stepLog({ message: 'I display offers' })
    cy.findByText('Afficher').click()
    cy.findByTestId('spinner').should('not.exist')

    cy.stepLog({
      message:
        'I search for "Établissement" with text "LYCEE POLYVALENT METIER ROBERT DOISNEAU"',
    })
    cy.findByTestId('select-omnisearch-criteria').select('Établissement')
    cy.findByTestId('omnisearch-filter-input-text').type(
      'LYCEE POLYVALENT METIER ROBERT DOISNEAU'
    )

    cy.stepLog({ message: 'These 6 results should be displayed' })
    const expectedResults = [
      [
        'Réservation',
        "Nom de l'offre",
        'Établissement',
        'Places et prix',
        'Statut',
      ],
      [
        '79',
        'offer',
        'LYCEE POLYVALENT METIER ROBERT DOISNEAU',
        '25 places100 €',
        'annulée',
      ],
      [
        '72',
        'offer',
        'LYCEE POLYVALENT METIER ROBERT DOISNEAU',
        '25 places100 €',
        'annulée',
      ],
      [
        '65',
        'offer',
        'LYCEE POLYVALENT METIER ROBERT DOISNEAU',
        '25 places100 €',
        'remboursée',
      ],
      [
        '58',
        'offer',
        'LYCEE POLYVALENT METIER ROBERT DOISNEAU',
        '25 places100 €',
        'terminée',
      ],
      [
        '51',
        'offer',
        'LYCEE POLYVALENT METIER ROBERT DOISNEAU',
        '25 places100 €',
        'confirmée',
      ],
      [
        '44',
        'offer',
        'LYCEE POLYVALENT METIER ROBERT DOISNEAU',
        '25 places100 €',
        'préréservée',
      ],
    ]
    expectOffersAreFound(expectedResults)
  })

  it('It should find collective bookings by booking number', () => {
    cy.stepLog({ message: 'I display offers' })
    cy.findByText('Afficher').click()
    cy.findByTestId('spinner').should('not.exist')

    cy.stepLog({
      message: 'I search for "Numéro de réservation" with text "66"',
    })
    cy.findByTestId('select-omnisearch-criteria').select(
      'Numéro de réservation'
    )
    cy.findByTestId('omnisearch-filter-input-text').type('66')

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
        '66',
        'offer',
        'ECOLE ELEMENTAIRE PUBLIQUE FRANCOIS MOISSON',
        '25 places100 €',
        'annulée',
      ],
    ]
    expectOffersAreFound(expectedResults)
  })

  // # @todo: faire un cas de recherche par date (comme dans https://github.com/pass-culture/pass-culture-main/pull/12931) + établissement
  // # Scenario: It should find collective bookings with two filters
  // #   When I fill venue with "real_venue 1 eac_2_lieu [BON EAC]"
  // #   And I display offers
  // #   And I search for "Établissement" with text "ECOLE ELEMENTAIRE PUBLIQUE FRANCOIS MOISSON"
  // #   Then These results should be displayed
  // #     | Réservation | Nom de l'offre | Établissement                               | Places et prix | Statut    |
  // #     |          80 | offer        | ECOLE ELEMENTAIRE PUBLIQUE FRANCOIS MOISSON | 25 places100 € | annulée   |
  // #     |          66 | offer        | ECOLE ELEMENTAIRE PUBLIQUE FRANCOIS MOISSON | 25 places100 € | annulée   |
  // #     |          52 | offer        | ECOLE ELEMENTAIRE PUBLIQUE FRANCOIS MOISSON | 25 places100 € | confirmée |
})
