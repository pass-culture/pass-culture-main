describe('Dummy test', () => {
  it('should login', () => {
    cy.login('pctest.admin93.0@example.com', 'user@AZERTY123').then(() => {
      cy.url().should('be.equal', 'http://localhost:3001/accueil')
    })
  })

  it('should login with WIP_RECURRENCE_FILTERS feature flag enabled', () => {
    cy.setFeatureFlags([{ name: 'WIP_RECURRENCE_FILTERS', isActive: true }])
      .login('pctest.admin93.0@example.com', 'user@AZERTY123')
      .then(() => {
        cy.url()
          .should('be.equal', 'http://localhost:3001/accueil')
          // reset FF to initial value after test
          .setFeatureFlags([
            { name: 'WIP_RECURRENCE_FILTERS', isActive: false },
          ])
      })
  })
})

export {}
