describe('Search collective offers', () => {
  const login = 'retention_structures@example.com'
  const password = 'user@AZERTY123'

  before(() => {
    cy.visit('/connexion')
    // cy.request({
    //   method: 'GET',
    //   url: 'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
    // }).then((response) => {
    //   login = response.body.user.email
    // })
  })

  it('A search with several filters should display expected results', () => {
    cy.login({
      email: login,
      password: password,
      redirectUrl: '/',
    })

    // I select offerer "eac_2_lieu [BON EAC]"
    cy.findByTestId('offerer-select').click()
    cy.findByText(/Changer de structure/).click()
    cy.findByTestId('offerers-selection-menu')
      .findByText('eac_2_lieu [BON EAC]')
      .click()
    cy.findByTestId('header-dropdown-menu-div').should('not.exist')
    cy.findAllByTestId('spinner').should('not.exist')

    // I go to Offres collectives view
    cy.intercept({ method: 'GET', url: '/collective/offers*', times: 1 }).as(
      'collectiveOffers'
    )
    cy.visit('/offres/collectives')
    cy.wait('@collectiveOffers')

    // I select "real_venue 1 eac_2_lieu [BON EAC]" in "Lieu"
    cy.findByLabelText('Lieu').select('real_venue 1 eac_2_lieu [BON EAC]')

    // I select "Projection audiovisuelle" in "Format"
    cy.findByLabelText('Format').select('Projection audiovisuelle')

    // I validate my collective filters
    cy.intercept({ method: 'GET', url: '/collective/offers*', times: 1 }).as(
      'collectiveOffers'
    )
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffers')

    // These 5 results should be displayed
    const data = [
      ['', '', 'Titre', 'Lieu', 'Établissement', 'Status'],
      [
        '',
        '',
        'offer',
        'real_venue 1 eac_2_lieu [BON EAC]',
        'Tous les établissements',
        'publiée',
      ],
      [
        '',
        '',
        'offer',
        'real_venue 1 eac_2_lieu [BON EAC]',
        'Tous les établissements',
        'publiée',
      ],
      [
        '',
        '',
        'offer',
        'real_venue 1 eac_2_lieu [BON EAC]',
        'Tous les établissements',
        'publiée',
      ],
      [
        '',
        '',
        'offer',
        'real_venue 1 eac_2_lieu [BON EAC]',
        'Tous les établissements',
        'publiée',
      ],
      [
        '',
        '',
        'offer',
        'real_venue 1 eac_2_lieu [BON EAC]',
        'Tous les établissements',
        'publiée',
      ],
    ]
    const nbreLines = data.length - 1
    const reLAbelCount = new RegExp(
      nbreLines + ' ' + '(offre|réservation)',
      'g'
    )

    cy.findAllByTestId('offer-item-row').should('have.length', nbreLines)
    cy.contains(reLAbelCount)

    for (let rowLine = 0; rowLine < nbreLines; rowLine++) {
      const bookLineArray = data[rowLine + 1]

      cy.findAllByTestId('offer-item-row')
        .eq(rowLine)
        .within(() => {
          cy.get('td').then(($elt) => {
            for (let column = 0; column < 6; column++) {
              cy.wrap($elt)
                .eq(column)
                .then((cellValue) => {
                  if (cellValue.text().length && bookLineArray[column].length) {
                    return cy
                      .wrap(cellValue)
                      .should('contain.text', bookLineArray[column])
                  } else {
                    return true
                  }
                })
            }
          })
        })
    }
  })
})
