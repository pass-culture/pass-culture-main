import { Then, When } from '@badeball/cypress-cucumber-preprocessor'

When('I fill in offer details', () => {
  cy.findByLabelText('Catégorie *').select('Spectacle vivant')
  cy.findByLabelText('Sous-catégorie *').select('Spectacle, représentation')
  cy.findByLabelText('Type de spectacle *').select('Théâtre')
  cy.findByLabelText('Sous-type *').select('Comédie')
  cy.findByLabelText('Titre de l’offre *').type('Le Diner de Devs')
  cy.findByLabelText('Description').type(
    'Une PO invite des développeurs à dîner...'
  )
  cy.findByText('Retrait sur place (guichet, comptoir...)').click()
  cy.findByLabelText('Email de contact *').type('passculture@example.com')
})

When('I validate offer details step', () => {
  cy.findByText('Enregistrer et continuer').click()
  cy.wait(['@getOffer', '@postOffer'])
})

When('I fill in prices', () => {
  cy.findByLabelText('Intitulé du tarif *').should('have.value', 'Tarif unique')
  cy.findByText('Ajouter un tarif').click()
  cy.findByText('Ajouter un tarif').click()

  cy.findByTestId('wrapper-priceCategories[0].label').within(() => {
    // trouve le premier champ avec le label:
    cy.findByLabelText('Intitulé du tarif *').type('Carré Or')
  })
  cy.findByTestId('wrapper-priceCategories[0].price').within(() => {
    // trouve le premier champ avec le label:
    cy.findByLabelText('Prix par personne *').type('100')
  })

  cy.findByTestId('wrapper-priceCategories[1].label').within(() => {
    // trouve le deuxième champ avec le label:
    cy.findByLabelText('Intitulé du tarif *').type('Fosse Debout')
  })
  cy.findByTestId('wrapper-priceCategories[1].price').within(() => {
    // trouve le deuxième champ avec le label:
    cy.findByLabelText('Prix par personne *').type('10')
  })

  cy.findByTestId('wrapper-priceCategories[2].label').within(() => {
    // trouve le troisième champ avec le label:
    cy.findByLabelText('Intitulé du tarif *').type('Fosse Sceptique')
  })
  // manque un data-testid ou un accessibility label
  cy.get('[name="priceCategories[2].free"]').click()

  cy.findByText('Accepter les réservations “Duo“').should('exist')
})

When('I validate prices step', () => {
  cy.findByText('Enregistrer et continuer').click()
  cy.wait(['@patchOffer', '@getOffer', '@getStocks'], {
    responseTimeout: 60 * 1000 * 3,
  })
})

When('I fill in recurrence', () => {
  cy.findByText('Ajouter une ou plusieurs dates').click()

  cy.findByText('Toutes les semaines').click()
  cy.findByLabelText('Vendredi').click()
  cy.findByLabelText('Samedi').click()
  cy.findByLabelText('Dimanche').click()
  cy.findByLabelText('Du *').type('2030-05-01')
  cy.findByLabelText('Au *').type('2030-09-30')
  cy.findByLabelText('Horaire 1 *').type('18:30')
  cy.findByText('Ajouter un créneau').click()
  cy.findByLabelText('Horaire 2 *').type('21:00')
  cy.findByText('Ajouter d’autres places et tarifs').click()
  cy.findByText('Ajouter d’autres places et tarifs').click()

  cy.findByTestId('wrapper-quantityPerPriceCategories[0].priceCategory').within(
    () => {
      // trouve la première liste déroulante avec le label:
      cy.findByLabelText('Tarif *').select('0,00\xa0€ - Fosse Sceptique')
    }
  )

  cy.findByTestId('wrapper-quantityPerPriceCategories[1].quantity').within(
    () => {
      // trouve le deuxième champ avec le label:
      cy.findByLabelText('Nombre de places').type('100')
    }
  )
  cy.findByTestId('wrapper-quantityPerPriceCategories[1].priceCategory').within(
    () => {
      // trouve la euxième liste déroulante avec le label:
      cy.findByLabelText('Tarif *').select('10,00\xa0€ - Fosse Debout')
    }
  )

  cy.findByTestId('wrapper-quantityPerPriceCategories[2].quantity').within(
    () => {
      // trouve le troisième champ avec le label:
      cy.findByLabelText('Nombre de places').type('20')
    }
  )
  cy.findByTestId('wrapper-quantityPerPriceCategories[2].priceCategory').within(
    () => {
      // trouve la troisième liste déroulante avec le label:
      cy.findByLabelText('Tarif *').select('100,00\xa0€ - Carré Or')
    }
  )

  // manque un data-testid ou un placeholder ou un label accessible
  cy.get('[name="bookingLimitDateInterval"]').type('3')
})

When('I validate recurrence step', () => {
  cy.findByText('Valider').click()
  cy.wait(['@postStocks'])

  cy.findByText('Enregistrer et continuer').click()
  cy.contains('Accepter les réservations "Duo" : Oui')
})

When('I publish my offer', () => {
  cy.findByText('Publier l’offre').click()
  cy.wait(['@patchOffer', '@getOffer'], {
    responseTimeout: 60 * 1000 * 2,
  })
})

Then('my new offer should be displayed', () => {
  cy.url().should('contain', '/offres')
  cy.contains('Le Diner de Devs')
  cy.contains('396 dates')
})
