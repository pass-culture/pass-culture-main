import { When, Then, Given } from '@badeball/cypress-cucumber-preprocessor'

Given('I display offers', () => {
    cy.findByText('Afficher').click()
})