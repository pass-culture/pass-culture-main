import * as signup from '../page-objects/signupPage';

describe('Account creation', () => {
  it('should create an account', () => {
    cy.visit('/inscription')

    // Fill in form
    signup.typeLastName('LEMOINE')
    signup.typeFirstName('Jean')
    signup.typeRandomisedEmail()
    signup.typePassword('ValidPassword12!')
    signup.typePhoneNumber('612345678')

    // Submit form
    cy.intercept({ method: 'POST', url: '/v2/users/signup/pro' }).as(
      'signupUser'
    )
    signup.clickOnSubmit()
    cy.wait('@signupUser')
    cy.url().should('contain', '/inscription/confirmation')
  })
})
