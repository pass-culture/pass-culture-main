import { When, Then, Given } from '@badeball/cypress-cucumber-preprocessor'

let offerText: string

Given('I go to adage login page with valid token', () => {
  cy.visit('/connexion')
  cy.getFakeAdageToken()
})

When('I open adage iframe', () => {
  const adageToken = Cypress.env('adageToken')
  cy.intercept({
    method: 'GET',
    url: '/adage-iframe/playlists/new_template_offers',
  }).as('new_template_offers')
  cy.visit(`/adage-iframe?token=${adageToken}`)
  cy.wait('@new_template_offers').its('response.statusCode').should('eq', 200)
  cy.findAllByTestId('spinner').should('not.exist')
})

When('I open adage iframe with venue', () => {
  const adageToken = Cypress.env('adageToken')
  cy.visit(`/adage-iframe?token=${adageToken}&venue=1`)
  cy.findAllByTestId('spinner').should('not.exist')
})

When('I open adage iframe with search page', () => {
  const adageToken = Cypress.env('adageToken')
  cy.setFeatureFlags([
    { name: 'WIP_ENABLE_ADAGE_VISUALIZATION', isActive: true },
  ])
  cy.intercept({
    method: 'GET',
    url: '/adage-iframe/collective/offers-template/60',
  }).as('offers_template')
  cy.visit(`/adage-iframe/recherche?token=${adageToken}`)
  cy.wait('@offers_template').its('response.statusCode').should('eq', 200)
  cy.findAllByTestId('spinner').should('not.exist')
})

When('I select first card domain', () => {
  cy.findAllByTestId('card-domain-link').first().click()
})

When('I select first displayed offer', () => {
  cy.findAllByTestId('card-offer-link').first().click()
})

When('I select first card venue', () => {
  cy.findAllByTestId('card-venue-link').first().scrollIntoView()

  cy.findAllByTestId('card-venue-link')
    .first()
    .within(() => {
      cy.findByTestId('venue-infos-name').then(($btn) => {
        const buttonLabel = $btn.text()
        cy.wrap(buttonLabel).as('buttonLabel')
      })
    })
  cy.findAllByTestId('card-venue-link').first().click()
})

When('I go back to search page', () => {
  cy.get('@buttonLabel').then((buttonLabel) => {
    cy.get(`button[title="Supprimer Lieu :  ${buttonLabel}"]`)
  })

  cy.findByRole('link', { name: 'Découvrir' }).click()

  cy.findByRole('link', { name: 'Rechercher' }).click()
})

When('I add first offer to favorites', () => {
  cy.findAllByTestId('card-offer')
    .first()
    .invoke('text')
    .then((text: string) => {
      offerText = text
      cy.intercept({
        method: 'POST',
        url: '/adage-iframe/logs/fav-offer/',
      }).as('fav-offer')
      cy.findAllByTestId('favorite-inactive').first().click()
      cy.wait('@fav-offer').its('response.statusCode').should('eq', 204)
      cy.findByTestId('global-notification-success').should(
        'contain',
        'Ajouté à vos favoris'
      )
    })
})

When('I chose grid view', () => {
  cy.findAllByTestId('toggle-button').click()
})

Then('the banner is displayed', () => {
  cy.get('[class^=_discovery-banner]').contains(
    'Découvrez la part collective du pass Culture'
  )
})

Then('the first offer should be added to favorites', () => {
  cy.contains('Mes Favoris').click()
  cy.contains(offerText)
})

When('the first favorite is unselected', () => {
  // à part de là c'est du afterScenario : on désélectionne le favori
  cy.findByRole('link', { name: 'Découvrir' }).click()
  // cy.reload()
  cy.intercept({
    method: 'DELETE',
    url: '/adage-iframe/collective/template/**/favorites',
  }).as('delete_fav')
  cy.findAllByTestId('favorite-active').first().click()
  cy.wait('@delete_fav').its('response.statusCode').should('eq', 204)
  cy.findByTestId('global-notification-success').should(
    'contain',
    'Supprimé de vos favoris'
  )
})

Then('the iframe should be displayed correctly', () => {
  cy.url().should('include', '/decouverte')
  cy.findAllByRole('link', { name: 'Découvrir' })
    .first()
    .should('have.attr', 'aria-current', 'page')
})

Then('the iframe search page should be displayed correctly', () => {
  cy.url().should('include', '/recherche')
  cy.findByRole('link', { name: 'Rechercher' }).should(
    'have.attr',
    'aria-current',
    'page'
  )
})

Then('the {string} button should be displayed', (button: string) => {
  cy.get('button').contains(button)
})

When(
  'I select {string} in {string} filter',
  (value: string, filter: string) => {
    cy.findByRole('button', { name: filter }).click()
    cy.findByLabelText(value).click()
    cy.findAllByRole('button', { name: 'Rechercher' }).first().click()
    cy.wait(500)
  }
)

Then(
  '{string} in {string} filter is selected',
  (value: string, filter: string) => {
    cy.findByRole('button', { name: filter }).click()
    cy.findByLabelText(value).should('be.checked')
    cy.wait(500)
  }
)

Then('I see no offer', () => {
  cy.findByText('Nous n’avons trouvé aucune offre publiée')
})

Then('offer descriptions are not displayed', () => {
  cy.findAllByTestId('offer-listitem')
  cy.findAllByTestId('offer-description').should('not.exist')
})

Then('offer descriptions are displayed', () => {
  cy.findAllByTestId('offer-listitem')
  cy.findAllByTestId('offer-description').should('exist')
})

When('I go to {string} menu', (menu: string) => {
  cy.contains(menu).click()
})
