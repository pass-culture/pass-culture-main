import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

When('I fill required information in create account form', () => {
  cy.findByLabelText('Nom *').type('LEMOINE')
  cy.findByLabelText('Prénom *').type('Jean')
  cy.findByLabelText('Adresse email *').type(`jean${Math.random()}@example.com`)
  cy.findByLabelText('Mot de passe *').type('ValidPassword12!')
  cy.findByPlaceholderText('6 12 34 56 78').type('612345678')
})

When('I submit', () => {
  cy.intercept({ method: 'POST', url: '/v2/users/signup/pro' }).as('signupUser')
  cy.findByText('Créer mon compte').click()
  cy.wait('@signupUser')
})

Then('my account should be created', () => {
    cy.url().should('contain', '/inscription/confirmation')
    // TODO: ajouter vérification sur le contenu de la page (et sur le retour API?)
    // on ne vérifie pas que le compte est bien créé
});
