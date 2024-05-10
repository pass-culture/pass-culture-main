import { When, Then, Given } from "@badeball/cypress-cucumber-preprocessor";

Given('I go to {string} page', (page: string) => {
    cy.visit('/'+page)
});

When("I fill required information in create account form", () => {
    cy.findByLabelText('Nom *').type('LEMOINE')
    cy.findByLabelText('Prénom *').type('Jean')
    cy.findByLabelText('Adresse email *').type(`jean${Math.random()}@example.com`)
    cy.findByLabelText('Mot de passe *').type('ValidPassword12!')
    cy.findByPlaceholderText('6 12 34 56 78').type('612345678')
});

When("I submit", () => {
    cy.intercept({ method: 'POST', url: '/v2/users/signup/pro' }).as(
        'signupUser'
      )
    cy.findByText('Créer mon compte').click()
    cy.wait('@signupUser')
});

Then('my account should be created', () => {
    cy.url().should('contain', '/inscription/confirmation')
});
