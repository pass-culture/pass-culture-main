describe('Account creation', () => {
  it('should create an account', () => {
    cy.visit('http://localhost:3001/inscription')

    // Fill in form
    cy.get('#lastName').type('LEMOINE')
    cy.get('#firstName').type('Jean')
    cy.get('#email').type(`jean${Math.random()}@example.com`)
    cy.get('#password').type('ValidPassword12!')
    cy.get('#countryCode').select('FR')
    cy.get('#phoneNumber').type('612345678')

    // Submit form
    cy.intercept({ method: 'POST', url: '/v2/users/signup/pro' }).as(
      'signupUser'
    )
    cy.get('button[type=submit]').click()
    cy.wait('@signupUser')
    cy.url().should(
      'be.equal',
      'http://localhost:3001/inscription/confirmation'
    )
  })
})
