import { Then, When } from '@badeball/cypress-cucumber-preprocessor'

When('I fill required information in create account form', () => {
  cy.findByLabelText('Nom *').type('LEMOINE')
  cy.findByLabelText('Prénom *').type('Jean')
  cy.findByLabelText('Adresse email *').type(`jean${Math.random()}@example.com`)
  cy.findByLabelText('Mot de passe *').type('ValidPassword12!')
  cy.findByPlaceholderText('6 12 34 56 78').type('612345678')
})

When('I submit', () => {
  cy.findByText('Créer mon compte').click()
})

Then('my account should be created', () => {
  cy.wait('@signupUser').its('response.statusCode').should('eq', 204)
  cy.url().should('contain', '/inscription/confirmation')
  cy.contains('Votre compte est en cours de création')
})
