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

    // Fill in SIREN
    cy.intercept(
      { method: 'GET', url: '/sirene/siren/*' },
      {
        address: {
          city: 'Paris',
          postalCode: '75001',
          street: '3 RUE DE VALOIS',
        },
        ape_code: '90.03A',
        name: 'MINISTERE DE LA CULTURE',
        siren: '306138900',
      }
    ).as('sirenApiCall')
    cy.get('#siren').type('306138900')
    cy.get('input[name=contactOk]').click() // We must tab out of the SIREN field for async validation to happen
    cy.wait('@sirenApiCall')

    // Submit form
    cy.intercept({ method: 'POST', url: '/users/signup/pro' }).as('signupUser')
    cy.get('button[type=submit]').click()
    cy.wait('@signupUser')
    cy.url().should(
      'be.equal',
      'http://localhost:3001/inscription/confirmation'
    )
  })
})
