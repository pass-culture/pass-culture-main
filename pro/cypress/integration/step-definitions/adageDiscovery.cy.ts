import { When, Then, Given } from "@badeball/cypress-cucumber-preprocessor";

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

Then("the iframe should be display correctly", () => {
    cy.url().should('include', '/decouverte')
    cy.findByRole('link', { name: 'Découvrir' }).should(
      'have.attr',
      'aria-current',
      'page'
    )
    cy.contains('Découvrez la part collective du pass Culture')
});

Then("the iframe search page should be display correctly", () => {
    cy.url().should('include', '/recherche')
    cy.findByRole('link', { name: 'Rechercher' }).should(
      'have.attr',
      'aria-current',
      'page'
    )
    cy.findByRole('button', { name: /Lieu : Librairie des GTls/ })
});