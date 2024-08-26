import { Then, When } from '@badeball/cypress-cucumber-preprocessor'

When('I open the first offer in the list', () => {
  cy.setFeatureFlags([{ name: 'WIP_SPLIT_OFFER', isActive: true }])
  cy.findAllByTestId('offer-item-row')
    .first()
    .within(() => {
      cy.findByRole('link', { name: 'Modifier' }).click()
    })
  cy.url().should('contain', '/recapitulatif')
})

When('I display Informations pratiques tab', () => {
  cy.findByText('Informations pratiques').click()
  cy.url().should('contain', '/pratiques')
})

When('I edit the offer displayed', () => {
  cy.get('a[aria-label^="Modifier les détails de l’offre"]').click()
  cy.url().should('contain', '/edition/pratiques')
})

When('I update the url link', () => {
  const randomUrl = `http://myrandomurl${Math.random().toString().substring(2, 5)}.fr/`
  cy.wrap(randomUrl).as('urlModified')
  cy.get('input#url').clear().type(randomUrl)
  cy.findByText('Enregistrer les modifications').click()
  cy.findAllByTestId('global-notification-success').should(
    'contain',
    'Vos modifications ont bien été enregistrées'
  )
  cy.findByText('Retour à la liste des offres').click()
  cy.url().should('contain', '/offres')
})

Then('the url updated is retrieved in the details of the offer', function () {
  cy.contains('URL d’accès à l’offre : ' + this.urlModified)
})
