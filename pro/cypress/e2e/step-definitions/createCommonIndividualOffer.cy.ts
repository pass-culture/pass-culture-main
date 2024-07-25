import { When } from '@badeball/cypress-cucumber-preprocessor'

When('I go to the offers list', () => {
  cy.findByText('Voir la liste des offres').click()
  cy.wait(
    [
      '@getOfferersNames',
      '@getOffer',
      '@getCategories',
      '@getVenuesForOfferer',
      '@getOffersForOfferer',
    ],
    {
      requestTimeout: 60 * 1000 * 5,
      responseTimeout: 60 * 1000 * 5,
    }
  )
})
