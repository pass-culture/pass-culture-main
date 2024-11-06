describe('Account creation', () => {
  it('I should be able to create an account', () => {
    cy.visit('/inscription')

    cy.stepLog({
      message: 'I fill required information in create account form',
    })
    cy.findByLabelText('Nom *').type('LEMOINE')
    cy.findByLabelText('Prénom *').type('Jean')
    cy.findByLabelText('Adresse email *').type(
      `jean${Math.random()}@example.com`
    )
    cy.findByLabelText('Mot de passe *').type('ValidPassword12!')
    cy.findByPlaceholderText('6 12 34 56 78').type('612345678')

    cy.stepLog({ message: 'I submit' })
    cy.intercept({ method: 'POST', url: '/v2/users/signup/pro' }).as(
      'signupUser'
    )
    cy.findByText('Créer mon compte').click()

    cy.stepLog({ message: 'my account should be created' })
    cy.wait('@signupUser').its('response.statusCode').should('eq', 204)
    cy.url().should('contain', '/inscription/confirmation')
    cy.contains('Votre compte est en cours de création')
  })
})
