describe('save filters so that you can retrieve them when you return to the search page', () => {
  beforeEach(() => {
    cy.visit('/connexion')
    cy.getFakeAdageToken()
  })

  it.only('should save view type in search page', () => {  // @TODO: pas migré ?
    const adageToken = Cypress.env('adageToken')
    cy.setFeatureFlags([
      { name: 'WIP_ENABLE_ADAGE_VISUALIZATION', isActive: true },
    ])
    cy.visit(`/adage-iframe/recherche?token=${adageToken}`)

    cy.findAllByTestId('offer-description')

    cy.findAllByTestId('toggle-button').click()
    cy.findAllByTestId('offer-description').should('not.exist')
    cy.contains('Mes Favoris').click()
    cy.contains('Rechercher').click()
    cy.findAllByTestId('offer-description').should('not.exist')
  })
})
