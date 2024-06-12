import { Given, Then, When } from '@badeball/cypress-cucumber-preprocessor'

When('I download reimbursement details', () => {
  cy.findByTestId('dropdown-menu-trigger').click()
  cy.findByText(/Télécharger le détail des réservations/).click()
})

// Does not work on CI: Error: connect ECONNREFUSED ::1:80
// Then('I can download accounting receipt as pdf', () => {
//   cy.findByTestId('dropdown-menu-trigger').click()
//   cy.findByText(/Télécharger le justificatif comptable/).then(function ($a) {
//     const href = $a.prop('href')
//     cy.request(href).its('body').should('not.be.empty')
//   })
// })

Then('I can see the reimbursement details', () => {
  const filename = `${Cypress.config('downloadsFolder')}/remboursements_pass_culture.csv`

  cy.readFile(filename, { timeout: 15000 }).should('not.be.empty')
})

Then('I can see information message about reimbursement', () => {
  cy.findByText("Les remboursements s'effectuent toutes les 2 à 3 semaines")
  cy.findByText(
    'Nous remboursons en un virement toutes les réservations validées entre le 1ᵉʳ et le 15 du mois, et lors d’un second toutes celles validées entre le 16 et le 31 du mois.'
  )
  cy.findByText(
    'Les offres de type événement se valident automatiquement 48h à 72h après leur date de réalisation, leurs remboursements peuvent se faire sur la quinzaine suivante.'
  )
})

Then('I can see a link to the next reimbursement help page', () => {
  cy.findByText(/En savoir plus sur les prochains remboursements/)
    .invoke('removeAttr', 'target') // removes target to not open it in a new tab (not supported by cypress)
    .click()
  cy.origin('https://passculture.zendesk.com', () => {
    // cloudfare/zendesk "Verify you are human" page cannot be used by cypress robot
    cy.url().should('include', '4411992051601')
  })
})

Then(
  'I can see a link to the terms and conditions of reimbursement help page',
  () => {
    cy.findByText(/Connaître les modalités de remboursement/)
      .invoke('removeAttr', 'target') // removes target to not open it in a new tab (not supported by cypress)
      .click()
    cy.origin('https://passculture.zendesk.com', () => {
      // cloudfare/zendesk "Verify you are human" page cannot be used by cypress robot
      cy.url().should('include', '4412007300369')
    })
  }
)
