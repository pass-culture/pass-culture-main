import { logAndGoToPage } from '../support/helpers.ts'

describe('Account creation', () => {
  it('I should be able to create an account', () => {
    const randomEmail = `jean${Math.random()}@example.com`
    cy.visit('/inscription')

    cy.stepLog({
      message: 'I fill required information in create account form',
    })
    cy.findByLabelText('Nom *').type('LEMOINE')
    cy.findByLabelText('Prénom *').type('Jean')
    cy.findByLabelText('Adresse email *').type(randomEmail)
    cy.findByLabelText('Mot de passe *').type('user@AZERTY123')
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

    cy.stepLog({ message: 'retrieve last email received' })
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/get_unique_email',
      // failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(200)
      expect(response.body.To).to.eq(randomEmail)
      cy.stepLog({ message: 'use the link in email to valide account' })
      cy.visit(response.body.params.EMAIL_VALIDATION_LINK)
    })

    cy.stepLog({
      message:
        'check that we are redirected to connexion with a toaster message',
    })
    cy.findAllByTestId('global-notification-success')
      .contains(
        'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.'
      )
      .should('not.be.visible')
    cy.url().should('contain', '/connexion')

    logAndGoToPage(randomEmail, '/parcours-inscription')
  })
})
