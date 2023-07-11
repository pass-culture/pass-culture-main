describe('Dummy test', () => {
  it('should login', () => {
    cy.setFeatureFlags([{ name: 'WIP_ENABLE_COOKIES_BANNER', isActive: false }])
      .login('pctest.admin93.0@example.com', 'user@AZERTY123')
      .url()
      .should('be.equal', 'http://localhost:3001/accueil')
      .setFeatureFlags([{ name: 'WIP_ENABLE_COOKIES_BANNER', isActive: true }])
  })

  it('should login with WIP_RECURRENCE_FILTERS feature flag enabled', () => {
    cy.setFeatureFlags([
      { name: 'WIP_RECURRENCE_FILTERS', isActive: true },
      { name: 'WIP_ENABLE_COOKIES_BANNER', isActive: false },
    ])
      .login('pctest.admin93.0@example.com', 'user@AZERTY123')
      .url()
      .should('be.equal', 'http://localhost:3001/accueil')
      // reset FF to initial value after test
      .setFeatureFlags([
        { name: 'WIP_RECURRENCE_FILTERS', isActive: false },
        { name: 'WIP_ENABLE_COOKIES_BANNER', isActive: true },
      ])
  })
})

export {}
