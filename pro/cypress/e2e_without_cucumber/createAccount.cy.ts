describe('Account creation', () => {
  it('should create an account', () => {
    cy.visit('/inscription')

    // Fill in form
    cy.findByLabelText('Nom *').type('LEMOINE')
    cy.findByLabelText('Prénom *').type('Jean')
    cy.findByLabelText('Adresse email *').type(
      `jean${Math.random()}@example.com`
    )
    cy.findByLabelText('Mot de passe *').type('ValidPassword12!')
    cy.findByPlaceholderText('6 12 34 56 78').type('612345678')

    // Submit form
    cy.intercept({ method: 'POST', url: '/v2/users/signup/pro' }).as(
      'signupUser'
    )
    cy.findByText('Créer mon compte').click()
    cy.wait('@signupUser')
    cy.url().should('contain', '/inscription/confirmation')
  })
})
