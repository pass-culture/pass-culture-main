describe('Account creation', () => {
  it('should create account', () => {
    cy.intercept({ method: 'POST', url: '/users/signup/pro' }).as('signupUser')

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

    cy.visit('http://localhost:3001/inscription')
      .get('#lastName')
      .type('LEMOINE')
      .get('#firstName')
      .type('Jean')
      .get('#email')
      .type(`jean${Math.random()}@example.com`)
      .get('#password')
      .type('ValidPassword12!')
      .get('#countryCode')
      .select('FR')
      .get('#phoneNumber')
      .type('612345678')
      .get('#siren')
      .type('306138900')
      .get('input[name=contactOk]')
      .click()
      .get('button[type=submit]')
      .click()

    cy.wait('@sirenApiCall')
      .wait('@signupUser')
      .then(() => {
        cy.url().should(
          'be.equal',
          'http://localhost:3001/inscription/confirmation'
        )
      })
  })
})

export {}
