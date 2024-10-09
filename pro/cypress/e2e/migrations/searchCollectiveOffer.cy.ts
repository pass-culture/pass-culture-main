describe('Search collective offers', () => {
  let login: string
  const password = 'user@AZERTY123'
  const venueName = 'Mon Lieu'
  const offerName = 'Mon offre collective'

  before(() => {
    cy.visit('/connexion')
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_pro_user_with_collective_offers',
    }).then((response) => {
      login = response.body.user.email
    })
    cy.intercept({ method: 'GET', url: '/collective/offers*' }).as(
      'collectiveOffers'
    )
  })

  it('A search with several filters should display expected results', () => {
    cy.login({
      email: login,
      password: password,
      redirectUrl: '/',
    })

    // I go to Offres collectives view
    cy.visit('/offres/collectives')
    cy.wait('@collectiveOffers')

    // I select "Mon Lieu" in "Lieu"
    cy.findByLabelText('Lieu').select(venueName)

    // I select "Projection audiovisuelle" in "Format"
    cy.findByLabelText('Format').select('Projection audiovisuelle')

    // I validate my collective filters
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffers')

    // These 5 results should be displayed
    const data = [
      ['', '', 'Titre', 'Lieu', 'Établissement', 'Status'],
      ['', '', offerName, venueName, 'Tous les établissements', 'publiée'],
    ]

    cy.findAllByTestId('offer-item-row').should('have.length', 1)
    cy.contains('1 offre')

    for (let rowLine = 0; rowLine < 1; rowLine++) {
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
