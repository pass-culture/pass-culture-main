describe('Signup journey', () => {
  const siret = Math.random().toString().substring(2, 16)

  const welcomeStep = () => {
    // Welcome page
    cy.visit({ method: 'GET', url: '/parcours-inscription' })
    cy.contains('Commencer').click()
  }

  const offererStep = () => {
    // Offerer page
    cy.intercept({
      method: 'GET',
      url: `http://localhost:5001/sirene/siret/${siret}`,
    }).as('getSiret')

    cy.get('#siret').type(siret)
    cy.contains('Continuer').click()
    cy.wait('@getSiret')
  }

  const activityStep = () => {
    // Activity page
    cy.get('#venueTypeCode').select('Spectacle vivant')
    cy.get('[name="socialUrls[0]"]').type('https://exemple.com')
    cy.contains('Ajouter un lien').click()
    cy.get('[name="socialUrls[1]"]').type('https://exemple2.com')

    cy.get('[name="targetCustomer.individual"]').check()
    cy.contains('Étape suivante').click()
  }

  const validationStep = () => {
    // Validation page
    cy.contains('Valider et créer ma structure').click()
    cy.url().should('be.equal', 'http://localhost:3001/accueil')
  }

  before(() => {
    cy.setFeatureFlags([{ name: 'WIP_ENABLE_NEW_ONBOARDING', isActive: true }])
  })

  it('should create offerer', () => {
    cy.login('pctest.pro93.0@example.com', 'user@AZERTY123')

    welcomeStep()
    offererStep()

    // Authentication page
    cy.get('#publicName').type('First Offerer')
    cy.contains('Étape suivante').click()

    activityStep()
    validationStep()

    cy.logout()
  })

  it('should ask offerer attachment to a user and create new offerer', () => {
    cy.login('pctest.pro97.0@example.com', 'user@AZERTY123')

    welcomeStep()
    offererStep()

    // Offerer attachment
    cy.contains('Ajouter une nouvelle structure').click()

    // Authentication page
    cy.get('#search-addressAutocomplete').clear()
    cy.get('#search-addressAutocomplete').type('89 Rue la Boétie 75008 Paris')
    cy.get('#list-addressAutocomplete li').first().click()
    cy.contains('Étape suivante').click()

    activityStep()
    validationStep()

    cy.logout()
  })

  after(() => {
    cy.setFeatureFlags([{ name: 'WIP_ENABLE_NEW_ONBOARDING', isActive: false }])
  })
})
