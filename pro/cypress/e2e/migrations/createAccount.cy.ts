/// <reference types="cypress-mailslurp" />

describe('Account creation', function () {
  before(function () {
    cy.log('Wrap inbox before test')
    void cy
      .mailslurp()
      .then((mailslurp) => mailslurp.createInbox())
      .then((inbox) => {
        cy.wrap(inbox.id).as('inboxId')
        cy.wrap(inbox.emailAddress).as('emailAddress')
        cy.log(`Inbox id ${inbox.id}`)
        cy.log(`Inbox email address: ${inbox.emailAddress}`)
      })
    // save inbox id and email address to this (make sure you use function and not arrow syntax)
  })

  it('should create an account', function () {
    cy.visit('/inscription')

    // I fill required information in create account form
    cy.findByLabelText('Nom *').type('LEMOINE')
    cy.findByLabelText('Prénom *').type('Jean')
    cy.findByLabelText('Adresse email *').type(this.emailAddress)
    cy.findByLabelText('Mot de passe *').type('ValidPassword12!')
    cy.findByPlaceholderText('6 12 34 56 78').type('612345678')

    // I submit
    cy.intercept({ method: 'POST', url: '/v2/users/signup/pro' }).as(
      'signupUser'
    )
    cy.findByText('Créer mon compte').click()

    // Then my account should be created
    cy.wait('@signupUser').its('response.statusCode').should('eq', 204)
    cy.url().should('contain', '/inscription/confirmation')
    cy.contains('Votre compte est en cours de création')
  })

  it('should send an email with validation', function () {
    void cy
      .mailslurp()
      .then((mailslurp) =>
        mailslurp.waitForLatestEmail(this.inboxId, 30000, true)
      )
  })
})
