import { When, Then, Given } from "@badeball/cypress-cucumber-preprocessor";

Given('I open {string} page', (page: string) => {
    cy.visit('/'+page)
});

Given("I am logged in", () => {
    cy.login({
        email: 'retention_structures@example.com',
        password: 'user@AZERTY123',
    })
});