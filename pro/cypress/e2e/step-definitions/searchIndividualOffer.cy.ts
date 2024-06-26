import { When, Then } from '@badeball/cypress-cucumber-preprocessor'
import dayjs from 'dayjs'

import customParseFormat from '../../../node_modules/dayjs/plugin/customParseFormat.js'

dayjs.extend(customParseFormat)

When('I search with the text {string}', (title: string) => {
  cy.findByPlaceholderText('Rechercher par nom d’offre ou par EAN-13').type(
    title
  )
  cy.findByText('Rechercher').click()
})

When('I select offerer {string} in offer page', (offererName: string) => {
  cy.intercept({ method: 'GET', url: '/venues?offererId=*' }).as('getOffererId')
  cy.findByTestId('offerer-select').click()
  cy.findByText(/Changer de structure/).click()
  cy.findByTestId('offerers-selection-menu').findByText(offererName).click()
  cy.wait('@getOffererId')
  cy.findAllByTestId('spinner').should('not.exist')
})

When('I select {string} in offer status', (filter: string) => {
  cy.findByTestId('wrapper-status').within(() => {
    cy.get('select').select(filter)
  })
})

When('I select a date in one month', () => {
  const dateSearch = dayjs().add(1, 'months').format('YYYY-MM-DD')
  cy.findByLabelText('Début de la période').type(dateSearch)
  cy.findByLabelText('Fin de la période').type(dateSearch)
})

Then('All filters are empty', () => {
  cy.findByPlaceholderText('Rechercher par nom d’offre ou par EAN-13').should(
    'be.empty'
  )
  cy.findByTestId('wrapper-lieu').within(() => {
    cy.get('select').invoke('val').should('eq', 'all')
  })
  cy.findByTestId('wrapper-categorie').within(() => {
    cy.get('select').invoke('val').should('eq', 'all')
  })
  cy.findByTestId('wrapper-creationMode').within(() => {
    cy.get('select').invoke('val').should('eq', 'all')
  })
  cy.findByTestId('wrapper-status').within(() => {
    cy.get('select').invoke('val').should('eq', 'all')
  })
  cy.findByLabelText('Début de la période').invoke('val').should('be.empty')
  cy.findByLabelText('Fin de la période').invoke('val').should('be.empty')
})

When('I reset all filters', () => {
  cy.findByText('Réinitialiser les filtres').click()
})
