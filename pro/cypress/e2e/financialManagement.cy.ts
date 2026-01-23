import { DEFAULT_AXE_CONFIG, DEFAULT_AXE_RULES } from '../support/constants.ts'
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

describe('Financial Management - messages, links to external help page, reimbursement details, unattach', () => {
  it('I should see information message about reimbursement', () => {
    cy.intercept({ method: 'GET', url: '/offerers/*' }).as('getOfferers')
    cy.intercept({ method: 'PATCH', url: 'offerers/*/bank-accounts/*' }).as(
      'patchBankAccount'
    )

    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_pro_user_with_financial_data',
      (response) => {
        logInAndGoToPage(response.body.user.email, '/remboursements')
      }
    )

    cy.stepLog({
      message: 'I can see information message about reimbursement',
    })
    cy.findByText("Les remboursements s'effectuent toutes les 2 à 3 semaines")
    cy.findByText(
      'Nous remboursons en un virement toutes les réservations validées entre le 1ᵉʳ et le 15 du mois, et lors d’un second toutes celles validées entre le 16 et le 31 du mois.'
    )
    cy.findByText(
      'Les offres de type événement se valident automatiquement 48h à 72h après leur date de réalisation, leurs remboursements peuvent se faire sur la quinzaine suivante.'
    )

    cy.stepLog({ message: 'no receipt results should be displayed' })
    cy.findAllByTestId('spinner').should('not.exist')
    cy.findAllByTestId('invoice-title-row').should('not.exist')
    cy.findAllByTestId('invoice-item-row').should('not.exist')
    cy.contains(
      'Vous n’avez pas encore de justificatifs de remboursement disponibles'
    )

    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)

    cy.stepLog({
      message: 'I can see a link to the next reimbursement help page',
    })

    cy.findByText(/En savoir plus sur les prochains remboursements/)

    cy.stepLog({
      message:
        'I can see a link to the terms and conditions of reimbursement help page',
    })

    cy.findByText(/Connaître les modalités de remboursement/)
  })

  describe('Data contains 1 offerer with 3 venues', () => {
    let login2: string
    beforeEach(() => {
      cy.visit('/connexion')
      cy.intercept({ method: 'GET', url: '/offerers/*' }).as('getOfferers')
      cy.intercept({ method: 'PATCH', url: 'offerers/*/bank-accounts/*' }).as(
        'patchBankAccount'
      )
      cy.sandboxCall(
        'GET',
        'http://localhost:5001/sandboxes/pro/create_pro_user_with_financial_data_and_3_venues',
        (response) => {
          login2 = response.body.user.email
          logInAndGoToPage(login2, 'remboursements/informations-bancaires')
        }
      )
    })

    it('I should be able to attach and unattach a few venues', () => {
      cy.findByTestId('profile-button')
      cy.findAllByTestId('spinner').should('not.exist')

      cy.stepLog({
        message: 'Attach all my venues',
      })
      cy.findByText('Rattacher une structure').click()

      cy.findByRole('dialog').within(() => {
        cy.findByText('Tout sélectionner').click()
        cy.findByText('Enregistrer').click()
      })

      attachmentModificationsDone()
      cy.stepLog({
        message: 'Unattach 2 in 4 venues',
      })
      cy.findByTestId('reimbursement-bank-account-linked-venues').within(() => {
        cy.contains('Structures rattachées à ce compte bancaire')
        cy.contains('Mon lieu 1')
        cy.contains('Mon lieu 2')
        cy.contains('Mon lieu 3')
        cy.findByText('Modifier').click()
      })

      cy.findByRole('dialog').within(() => {
        cy.findByText('Mon lieu 1').click()
        cy.findByText('Mon lieu 2').click()
        cy.findByText('Enregistrer').click()
        cy.contains(
          'Attention : la ou les structures désélectionnées ne seront plus remboursées sur ce compte bancaire'
        )
        cy.findByText('Confirmer').click()
      })

      attachmentModificationsDone()

      cy.stepLog({
        message: 'Check only Mon lieu 3 is attached',
      })
      cy.findByTestId('reimbursement-bank-account-linked-venues').within(
        ($elt) => {
          cy.contains('Structure rattachée à ce compte bancaire')
          cy.contains('Certaines de vos structures ne sont pas rattachées.')
          cy.get('div').contains('Mon lieu 3')
          cy.wrap($elt)
            .should('not.contain', 'Mon lieu 1')
            .and('not.contain', 'Mon lieu 2')
        }
      )
    })
    it('I should be able to attach and unattach all venues', () => {
      cy.findByTestId('profile-button')
      cy.findAllByTestId('spinner').should('not.exist')

      cy.stepLog({
        message: 'Attach all my venues',
      })
      cy.findByText('Rattacher une structure').click()

      cy.findByRole('dialog').within(() => {
        cy.findByText('Tout sélectionner').click()
        cy.findByText('Enregistrer').click()
      })

      attachmentModificationsDone()
      cy.stepLog({
        message: 'Unattach all venues',
      })

      cy.contains('Structures rattachées à ce compte bancaire')
      cy.findByText('Modifier').click()
      cy.findByRole('dialog').within(() => {
        cy.findByText('Tout désélectionner').click()
        cy.findByText('Enregistrer').click()
        cy.contains(
          'Attention : la ou les structures désélectionnées ne seront plus remboursées sur ce compte bancaire'
        )
        cy.findByText('Confirmer').click()
      })

      attachmentModificationsDone()

      cy.stepLog({
        message: 'Check no venues attached',
      })
      cy.findByTestId('reimbursement-bank-account-linked-venues').within(
        ($elt) => {
          cy.contains('Structure rattachée à ce compte bancaire')
          cy.contains('Aucune structure n’est rattachée à ce compte bancaire.')
          cy.wrap($elt)
            .should('not.contain', 'Mon lieu 1')
            .and('not.contain', 'Mon lieu 2')
            .and('not.contain', 'Mon lieu 3')
        }
      )
    })
  })
})
