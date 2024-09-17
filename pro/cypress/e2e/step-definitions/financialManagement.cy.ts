import { DataTable, Then, When } from '@badeball/cypress-cucumber-preprocessor'

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

When('I remove {string} venue from my bank account', (venue: string) => {
  cy.findByTestId('reimbursement-bank-account-linked-venues').within(() => {
    cy.contains('Lieu(x) rattaché(s) à ce compte bancaire')
    cy.contains('Certains de vos lieux ne sont pas rattachés.')
    cy.contains(venue)

    cy.findByText('Modifier').click()
  })

  cy.findByRole('dialog').within(() => {
    cy.findByLabelText(venue).should('be.checked')
    cy.findByLabelText(venue).uncheck()
    cy.findByText('Enregistrer').click()
    cy.intercept({ method: 'GET', url: '/offerers/*' }).as('getOfferers')
    cy.findByText('Confirmer').click()
    cy.wait('@getOfferers').its('response.statusCode').should('equal', 200)
  })
})

When('I add {string} venue to my bank account', (venue: string) => {
  cy.findByTestId('reimbursement-bank-account-linked-venues').within(() => {
    cy.findByText('Rattacher un lieu').click()
  })

  cy.intercept({ method: 'PATCH', url: 'offerers/*/bank-accounts/*' }).as(
    'patchOfferer'
  )

  cy.findByRole('dialog').within(() => {
    cy.findByLabelText(venue).should('not.be.checked')
    cy.findByLabelText(venue).check()

    cy.findByText('Enregistrer').click()
  })

  cy.wait('@patchOfferer').its('response.statusCode').should('equal', 204)
})

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
  cy.url().then((url: string) => {
    cy.findByText(/En savoir plus sur les prochains remboursements/)
      .invoke('removeAttr', 'target') // removes target to not open it in a new tab (not supported by cypress)
      .click()
    // En local, ne marche pas, il faut remplacer par
    //     cy.origin('https://aide.passculture.app', () => {
    cy.origin('https://passculture.zendesk.com', () => {
      // cloudfare/zendesk "Verify you are human" page cannot be used by cypress robot
      cy.url().should('include', '4411992051601')
    })
    cy.visit(url)
  })
})

Then(
  'I can see a link to the terms and conditions of reimbursement help page',
  () => {
    cy.url().then((url: string) => {
      cy.findByText(/Connaître les modalités de remboursement/)
        .invoke('removeAttr', 'target') // removes target to not open it in a new tab (not supported by cypress)
        .click()
      // En local, ne marche pas, il faut remplacer par
      //     cy.origin('https://aide.passculture.app', () => {
      cy.origin('https://passculture.zendesk.com', () => {
        // cloudfare/zendesk "Verify you are human" page cannot be used by cypress robot
        cy.url().should('include', '4412007300369')
      })
      cy.visit(url)
    })
  }
)

Then('These receipt results should be displayed', (dataTable: DataTable) => {
  const numRows = dataTable.rows().length
  const numColumns = dataTable.raw()[0].length
  const data = dataTable.raw()

  cy.findAllByTestId('spinner').should('not.exist')
  cy.findAllByTestId('invoice-item-row').should('have.length', numRows)

  // Vérification des titres des colonnes
  const titleArray = data[0]
  cy.findAllByTestId('invoice-title-row').within(() => {
    cy.get('th').then(($elt) => {
      for (let column = 0; column < numColumns; column++) {
        if (titleArray[column] !== '') {
          cy.wrap($elt).eq(column).should('contain', titleArray[column])
        }
      }
    })
  })

  // Vérification du contenu du tableau
  for (let rowLine = 0; rowLine < numRows; rowLine++) {
    const bookLineArray = data[rowLine + 1]

    cy.findAllByTestId('invoice-item-row')
      .eq(rowLine)
      .within(() => {
        cy.get('td').then(($elt) => {
          for (let column = 0; column < numColumns; column++) {
            if (bookLineArray[column] !== '') {
              cy.wrap($elt).eq(column).should('contain', bookLineArray[column])
            }
          }
        })
      })
  }
})

Then('No receipt results should be displayed', () => {
  cy.findAllByTestId('spinner').should('not.exist')
  cy.findAllByTestId('invoice-title-row').should('not.exist')
  cy.findAllByTestId('invoice-item-row').should('not.exist')
  cy.contains(
    'Vous n’avez pas encore de justificatifs de remboursement disponibles'
  )
})

Then('no venue should be linked to my account', () => {
  cy.findAllByTestId('global-notification-success').should(
    'contain',
    'Vos modifications ont bien été prises en compte.'
  )
  cy.findAllByTestId('spinner').should('not.exist')
  cy.findByTestId('reimbursement-bank-account-linked-venues').within(() => {
    cy.contains('Aucun lieu n’est rattaché à ce compte bancaire.')
  })
})

Then('{string} venue should be linked to my account', (venue: string) => {
  cy.findAllByTestId('global-notification-success').should(
    'contain',
    'Vos modifications ont bien été prises en compte.'
  )
  cy.findAllByTestId('spinner').should('not.exist')
  cy.findByTestId('reimbursement-bank-account-linked-venues').within(() => {
    cy.contains('Lieu(x) rattaché(s) à ce compte bancaire')
    cy.contains('Certains de vos lieux ne sont pas rattachés.')
    cy.contains(venue)
  })
})
