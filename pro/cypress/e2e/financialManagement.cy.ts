describe('Financial Management - messages, links to external help page, reimbursement details', () => {
  let login: string
  const password = 'user@AZERTY123'

  beforeEach(() => {
    cy.visit('/connexion')
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_pro_user_with_financial_data',
    }).then((response) => {
      login = response.body.user.email
    })
    cy.intercept({ method: 'GET', url: '/offerers/*' }).as('getOfferers')
    cy.intercept({ method: 'PATCH', url: 'offerers/*/bank-accounts/*' }).as(
      'patchBankAccount'
    )
  })

  it('Check messages, reimbursement details and offerer selection change', () => {
    cy.stepLog({ message: 'I am logged in' })
    cy.login({
      email: login,
      password: password,
      redirectUrl: '/',
    })

    cy.stepLog({ message: 'I go to the "Gestion financière" page' })
    cy.findAllByText('Gestion financière').first().click()
    cy.url().should('contain', '/remboursements')

    cy.stepLog({ message: 'I can see information message about reimbursement' })
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

    cy.stepLog({
      message: 'I can see a link to the next reimbursement help page',
    })
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

    cy.stepLog({
      message:
        'I can see a link to the terms and conditions of reimbursement help page',
    })
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

    cy.stepLog({
      message: 'I select offerer "Structure avec informations bancaires"',
    })
    cy.findByTestId('offerer-select').click()
    cy.findByText(/Changer de structure/).click()
    cy.findByTestId('offerers-selection-menu')
      .findByText('Structure avec informations bancaires')
      .click()
    cy.findByTestId('header-dropdown-menu-div').should('not.exist')
    cy.findAllByTestId('spinner').should('not.exist')

    cy.stepLog({ message: 'These receipt results should be displayed' })
    const data = [
      [
        'Date du justificatif',
        'Type de document',
        'Compte bancaire',
        'N° de virement',
        'Montant remboursé',
        'Actions',
      ],
      [
        '',
        '',
        'Trop perçu',
        'Libellé des coordonnées bancaires n°0',
        'N/A',
        '-10,00',
      ],
    ]
    const numRows = data.length - 1
    const numColumns = data[0].length

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

    cy.stepLog({ message: 'I download reimbursement details' })
    cy.findByTestId('dropdown-menu-trigger').click()
    cy.findByText(/Télécharger le détail des réservations/).click()

    cy.stepLog({ message: 'I can see the reimbursement details' })
    const filename = `${Cypress.config('downloadsFolder')}/remboursements_pass_culture.csv`
    cy.readFile(filename, { timeout: 15000 }).should('not.be.empty')
  })

  it('Automatic link venue with bank account', () => {
    cy.stepLog({ message: 'I am logged in' })
    cy.login({
      email: login,
      password: password,
      redirectUrl: '/',
    })
    cy.findByTestId('offerer-select')
    cy.wait('@getOfferers').its('response.statusCode').should('equal', 200)
    cy.findAllByTestId('spinner').should('not.exist')

    cy.stepLog({
      message: 'I select offerer "Structure avec informations bancaires"',
    })

    cy.findByTestId('offerer-select').click()
    cy.findByText(/Changer de structure/).click()
    cy.findByTestId('offerers-selection-menu')
      .findByText('Structure avec informations bancaires')
      .click()
    cy.wait('@getOfferers').its('response.statusCode').should('equal', 200)
    cy.findByTestId('header-dropdown-menu-div').should('not.exist')
    cy.findAllByTestId('spinner').should('not.exist')

    cy.stepLog({ message: 'I go to the "Gestion financière" page' })
    cy.findAllByText('Gestion financière').first().click()
    cy.url().should('contain', '/remboursements')

    cy.stepLog({ message: 'I go to "Informations bancaires" view' })
    cy.findByText('Informations bancaires').click()
    cy.findAllByTestId('spinner').should('not.exist')

    cy.stepLog({
      message: 'I remove "Mon Lieu" venue from my bank account',
    })
    const venue = 'Mon Lieu'
    cy.findByText('Aucun lieu n’est rattaché à ce compte bancaire.')
    cy.findByText('Rattacher un lieu').click()

    cy.findByRole('dialog').within(() => {
      cy.findByText(venue).click()
      cy.findByText('Enregistrer').click()
    })
    cy.wait('@getOfferers').its('response.statusCode').should('equal', 200)
    cy.findByRole('dialog').should('not.exist')

    cy.findByTestId('reimbursement-bank-account-linked-venues').within(() => {
      cy.contains('Lieu(x) rattaché(s) à ce compte bancaire')
      cy.contains(venue)
      cy.findByText('Modifier').click()
    })

    cy.findByRole('dialog').within(() => {
      cy.findByLabelText(venue).should('be.checked')
      cy.findByLabelText(venue).uncheck()
      cy.findByText('Enregistrer').click()
      cy.contains(
        'Attention : le ou les lieux désélectionnés ne seront plus remboursés sur ce compte bancaire'
      )
      cy.findByText('Confirmer').click()
    })
    cy.wait('@getOfferers').its('response.statusCode').should('equal', 200)
    cy.findByRole('dialog').should('not.exist')

    cy.stepLog({ message: 'no venue should be linked to my account' })
    cy.findAllByTestId('global-notification-success').should(
      'contain',
      'Vos modifications ont bien été prises en compte.'
    )
    cy.findAllByTestId('spinner').should('not.exist')
    cy.findByTestId('reimbursement-bank-account-linked-venues').within(() => {
      cy.contains('Aucun lieu n’est rattaché à ce compte bancaire.')
    })

    cy.stepLog({
      message: 'I add "Mon Lieu" venue to my bank account',
    })
    cy.findByTestId('reimbursement-bank-account-linked-venues').within(() => {
      cy.findByText('Rattacher un lieu').click()
    })

    cy.findByRole('dialog').within(() => {
      cy.findByLabelText(venue).should('not.be.checked')
      cy.findByLabelText(venue).check()

      cy.findByText('Enregistrer').click()
    })
    cy.wait(['@getOfferers', '@patchBankAccount']).then((interception) => {
      if (interception[0].response) {
        expect(interception[0].response.statusCode).to.equal(200)
      }
      if (interception[1].response) {
        expect(interception[1].response.statusCode).to.equal(204)
      }
    })
    cy.findByRole('dialog').should('not.exist')

    cy.stepLog({
      message: '"Mon Lieu" venue should be linked to my account',
    })
    cy.findAllByTestId('global-notification-success').should(
      'contain',
      'Vos modifications ont bien été prises en compte.'
    )
    cy.findAllByTestId('spinner').should('not.exist')
    cy.findByTestId('reimbursement-bank-account-linked-venues').within(() => {
      cy.contains('Lieu(x) rattaché(s) à ce compte bancaire')
      cy.contains(venue)
    })
  })
})
