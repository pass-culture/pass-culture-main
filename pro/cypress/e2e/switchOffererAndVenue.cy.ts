import { logInAndGoToPage } from '../support/helpers.ts'

export function attachmentModificationsDone() {
  cy.stepLog({
    message: 'Modifications done',
  })
  cy.findAllByTestId(`global-snack-bar-success-0`).should(
    'contain',
    'Vos modifications ont bien été prises en compte.'
  )
  cy.findByRole('dialog').should('not.exist')
}

describe('Switch Offerer and Venue', () => {
  it('I should be redirected to the onboarding page when I switch to an offerer not onboarded yet', () => {
    cy.intercept({ method: 'GET', url: '/offerers/*' }).as('getOfferers')
    cy.intercept({ method: 'PATCH', url: 'offerers/*/bank-accounts/*' }).as(
      'patchBankAccount'
    )

    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_pro_user_with_1_onboarded_and_1_unonboarded_offerers',
      (response) => {
        logInAndGoToPage(response.body.user.email, '/offres')
      }
    )

    cy.stepLog({
      message: 'I can visit the offers page',
    })
    cy.findByRole('heading', { level: 1, name: 'Offres individuelles' })

    cy.stepLog({
      message: 'I select offerer "Unonboarded Offerer"',
    })
    cy.findByTestId('profile-button').click()
    cy.findByText(/Changer/).click()
    cy.findByTestId('offerers-selection-menu')
      .findByText('Unonboarded Offerer')
      .click()
    cy.findByTestId('header-dropdown-menu-div').should('not.exist')
    cy.findAllByTestId('spinner').should('not.exist')

    cy.stepLog({
      message: 'We should be redirected on the onboarding page',
    })
    cy.findByRole('heading', {
      level: 1,
      name: 'Bienvenue sur le pass Culture Pro !',
    })
    cy.findByRole('heading', {
      level: 2,
      name: 'Où souhaitez-vous diffuser votre première offre ?',
    })
  })
})
