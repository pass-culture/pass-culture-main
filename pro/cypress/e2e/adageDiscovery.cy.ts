describe('Adage discovery', () => {
  beforeEach(() => {
    cy.visit('/connexion')
    cy.setFeatureFlags([{ name: 'WIP_ENABLE_DISCOVERY', isActive: true }])
    cy.getFakeAdageToken()
  })

  it('should redirect to adage discovery', () => {
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)
    cy.contains('Découvrez la part collective du pass Culture')
  })
})
