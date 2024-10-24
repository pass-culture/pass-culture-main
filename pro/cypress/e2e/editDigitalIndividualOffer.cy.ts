import { logAndGoToPage } from '../support/helpers.ts'

describe('Edit a digital individual offer', () => {
  let login: string

  beforeEach(() => {
    cy.visit('/connexion')
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_regular_pro_user_with_virtual_offer',
    }).then((response) => {
      login = response.body.user.email
      cy.setFeatureFlags([{ name: 'WIP_SPLIT_OFFER', isActive: true }])
    })
  })

  it('An edited offer is displayed with 4 tabs', function () {
    logAndGoToPage(login, '/offre/individuelle/1/recapitulatif/details')

    cy.contains('Récapitulatif')

    cy.stepLog({ message: 'I check that the 4 tab are displayed' })
    cy.findByRole('tablist').within(() => {
      cy.findAllByRole('tab').eq(0).should('have.text', 'Détails de l’offre')
      cy.findAllByRole('tab')
        .eq(1)
        .should('have.text', 'Informations pratiques')
      cy.findAllByRole('tab').eq(2).should('have.text', 'Stock & Prix')
      cy.findAllByRole('tab').eq(3).should('have.text', 'Réservations')
    })
  })

  it('I should be able to modify the url of a digital offer', function () {
    logAndGoToPage(login, '/offres')

    cy.stepLog({ message: 'I open the first offer in the list' })
    cy.findAllByTestId('offer-item-row')
      .first()
      .within(() => {
        cy.findByRole('link', { name: 'Modifier' }).click()
      })
    cy.url().should('contain', '/recapitulatif')

    cy.stepLog({ message: 'I display Informations pratiques tab' })
    cy.findByText('Informations pratiques').click()
    cy.url().should('contain', '/pratiques')

    cy.stepLog({ message: 'I edit the offer displayed' })
    cy.get('a[aria-label^="Modifier les détails de l’offre"]').click()
    cy.url().should('contain', '/edition/pratiques')

    cy.stepLog({ message: 'I update the url link' })
    const randomUrl = `http://myrandomurl.fr/`
    cy.get('input#url').clear().type(randomUrl)
    cy.findByText('Enregistrer les modifications').click()
    cy.findAllByTestId('global-notification-success').should(
      'contain',
      'Vos modifications ont bien été enregistrées'
    )
    cy.findByText('Retour à la liste des offres').click()
    cy.url().should('contain', '/offres')
    cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')
    cy.contains('Offres individuelles')

    cy.stepLog({ message: 'I open the first offer in the list' })
    cy.findAllByTestId('offer-item-row')
      .first()
      .within(() => {
        cy.findByRole('link', { name: 'Modifier' }).click()
      })
    cy.url().should('contain', '/recapitulatif')

    cy.stepLog({ message: 'I display Informations pratiques tab' })
    cy.findByText('Informations pratiques').click()
    cy.url().should('contain', '/pratiques')

    cy.stepLog({
      message: 'the url updated is retrieved in the details of the offer',
    })
    cy.contains('URL d’accès à l’offre : ' + randomUrl)
  })
})
