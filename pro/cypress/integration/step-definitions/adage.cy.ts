import { When, Then, Given } from "@badeball/cypress-cucumber-preprocessor";

let offerText: string

Given("I go to adage login page with valide token", () => {
    cy.visit('/connexion')
    cy.getFakeAdageToken()

    cy.intercept({
      method: 'GET',
      url: 'adage-iframe/playlists/new_template_offers',
    }).as('getNewTemplateOffersPlaylist')
});

When("I open adage iframe", () => {
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}`)
});

When("I open adage iframe with search page", () => {
    const adageToken = Cypress.env('adageToken')
    cy.visit(`/adage-iframe?token=${adageToken}&venue=1`)
});

When("I select first card domain", () => {
  cy.findAllByTestId('card-domain-link').first().click()
});

When("I select first displayed offer", () => {
  cy.findAllByTestId('card-offer-link').first().click()
});

When("I select first card venue", () => {
  cy.findAllByTestId('card-venue-link').first().scrollIntoView()

  cy.findAllByTestId('card-venue-link').first().within(($cardVenuelink) => {
    cy.findByTestId('venue-infos-name').then($btn => {
      const buttonLabel = $btn.text()
      cy.wrap(buttonLabel).as('buttonLabel')
    })
  })
  cy.findAllByTestId('card-venue-link').first().click()
});

When("I go back to search page", () => {
  cy.get('@buttonLabel').then(buttonLabel => {
    cy.get(`button[title="Supprimer Lieu :  ${buttonLabel}"]`)
  })

  cy.findByRole('link', { name: 'Découvrir' }).click()

  cy.findByRole('link', { name: 'Rechercher' }).click()
});

When("I add first offer to favorites", () => {
  cy.findAllByTestId('card-offer')
  .first()
  .invoke('text')
  .then((text: string) => {
    offerText = text

    cy.findAllByTestId('favorite-inactive').first().click()
    cy.contains('Ajouté à vos favoris')
  })
});

Then("the banner is displayed", () => {
  cy.get('[class^=_discovery-banner]')
    .contains('Découvrez la part collective du pass Culture')
});

Then("the first offer should be added to favorites", () => {

  cy.contains('Mes Favoris').click()

  cy.contains(offerText)

  // à part de là c'est du afterScenario : on désélectionne le favori
  cy.findByRole('link', { name: 'Découvrir' }).click()

  cy.reload()

  cy.findAllByTestId('favorite-active').first().click()
});

Then("the iframe should be display correctly", () => {
    cy.url().should('include', '/decouverte')
    cy.findAllByRole('link', { name: 'Découvrir' }).first().should(
      'have.attr',
      'aria-current',
      'page'
    )
});

Then("the iframe search page should be display correctly", () => {
    cy.url().should('include', '/recherche')
    cy.findByRole('link', { name: 'Rechercher' }).should(
      'have.attr',
      'aria-current',
      'page'
    )
});

Then('the {string} button should be displayed', (button: string) => {
  cy.get('button').contains(button)
});

When("I select {string} in {string} filter", (value: string, filter: string) => {
    cy.findByRole('button', { name: filter }).click()
    cy.findByLabelText(value).click()
    cy.findAllByRole('button', { name: 'Rechercher' }).first().click()
    cy.wait(500)
});

Then('I see no offer', () => {
    cy.findByText('Nous n’avons trouvé aucune offre publiée')
});

When('I go to {string} menu', (menu: string) => {
    cy.contains(menu).click()
});
  
When("stuff happens", () => {
    // cy.findByRole('button', { name: 'Format' }).click()
    // cy.findByLabelText('Atelier de pratique').click()
    // cy.findAllByRole('button', { name: 'Rechercher' }).eq(1).click()
    // cy.findByRole('button', { name: 'Domaine artistique' }).click()
    // cy.findByLabelText('Arts numériques').click()
    // cy.findAllByRole('button', { name: 'Rechercher' }).eq(1).click()
    //cy.findByText('Nous n’avons trouvé aucune offre publiée')

    cy.pause()
    // cy.contains('Mes Favoris').click()
    cy.contains('Rechercher').click()
    cy.findByRole('button', { name: 'Format (1)' }).click()
    cy.findByLabelText('Atelier de pratique').should('be.checked')
    cy.findByRole('button', { name: 'Domaine artistique (1)' }).click()
    cy.findByLabelText('Arts numériques').should('be.checked')
    cy.findByText('Nous n’avons trouvé aucune offre publiée')
});