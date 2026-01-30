import { DEFAULT_AXE_CONFIG, DEFAULT_AXE_RULES } from '../support/constants.ts'

describe('Account creation', () => {
  before(() => {
    cy.visit('/')
  })

  beforeEach(() => {
    cy.visit('/inscription/compte/creation')
    cy.injectAxe(DEFAULT_AXE_CONFIG)

    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/clear_email_list',
      (response) => {
        expect(response.status).to.eq(200)
      }
    )
  })

  it('I should be able to create an account', () => {
    const randomEmail = `jean${Math.random()}@example.com`
    cy.stepLog({
      message: 'I fill required information in create account form',
    })
    cy.findByLabelText(/Nom/).type('LEMOINE')
    cy.findByLabelText(/Prénom/).type('Jean')
    cy.findByLabelText(/Adresse email/).type(randomEmail)
    cy.findByLabelText(/Mot de passe/).type('user@AZERTY123')

    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)

    cy.stepLog({ message: 'I submit' })
    cy.intercept({ method: 'POST', url: '/users/signup' }).as('signupUser')
    cy.findByText('S’inscrire').click()

    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)

    cy.stepLog({ message: 'my account should be created' })
    cy.wait('@signupUser').its('response.statusCode').should('eq', 204)
    cy.url().should('contain', '/inscription/compte/confirmation')
    cy.contains('Validez votre adresse email')

    cy.stepLog({ message: 'retrieve last email received' })

    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/get_unique_email',
      (response) => {
        expect(response.status).to.eq(200)
        expect(response.body.To).to.eq(randomEmail)
        cy.stepLog({ message: 'use the link in email to valide account' })
        cy.visit(response.body.params.EMAIL_VALIDATION_LINK)
        cy.injectAxe(DEFAULT_AXE_CONFIG)
      }
    )

    cy.stepLog({
      message: 'check that we are redirected to connexion',
    })
    cy.url().should('contain', '/inscription/structure/recherche')
    cy.findByRole('link', { name: /Aller au contenu/ }).should('have.focus')
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
  })
})
