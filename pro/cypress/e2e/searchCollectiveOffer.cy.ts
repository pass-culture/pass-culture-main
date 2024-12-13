import { addWeeks, format } from 'date-fns'

import {
  expectOffersOrBookingsAreFound,
  sessionLogInAndGoToPage,
} from '../support/helpers.ts'

describe('Search collective offers', () => {
  let login: string
  let offerPublishedTemplate: { "name": string, "venueName": string }
  let offerPublished: { "name": string, "venueName": string }
  let offerDraft: { "name": string, "venueName": string }
  let offerInInstruction: { "name": string, "venueName": string }
  let offerNotConform: { "name": string, "venueName": string }
  let offerArchived: { "name": string, "venueName": string }

  const formatName = 'Concert'

  before(() => {
    cy.visit('/connexion')
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_pro_user_with_collective_offers',
    }).then((response) => {
      login = response.body.user.email
      offerPublishedTemplate = response.body.offerPublishedTemplate
      offerPublished = response.body.offerPublished
      offerDraft = response.body.offerDraft
      offerInInstruction = response.body.offerInInstruction
      offerNotConform = response.body.offerNotConform
      offerArchived = response.body.offerArchived
    })
    cy.setFeatureFlags([
      { name: 'ENABLE_COLLECTIVE_NEW_STATUSES', isActive: true },
    ])
  })

  beforeEach(() => {
    sessionLogInAndGoToPage(
      'Session search collective offer',
      login,
      '/accueil'
    )

    cy.intercept({ method: 'GET', url: '/collective/offers*' }).as(
      'collectiveOffers'
    )
    cy.intercept({ method: 'GET', url: '/venues?offererId*' }).as(
      'venuesOffererId'
    )
    cy.visit('/offres/collectives')
    cy.wait(['@collectiveOffers', '@venuesOffererId'])
    cy.findAllByTestId('spinner').should('not.exist')
  })

  it(`I should be able to search with a name and see expected results`, () => {
    cy.stepLog({
      message: 'I search with the name "' + offerPublished.name + '"',
    })
    cy.findByPlaceholderText('Rechercher par nom d’offre').type(
      offerPublished.name
    )

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      ['', '', 'Titre', 'Lieu', 'Établissement', 'Statut'],
      ['', '', offerPublished.name, offerPublished.venueName, '', 'publiée'],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it(`I should be able to search with a lieu and see expected results`, () => {
    cy.stepLog({ message: 'I search with the place "' + offerArchived.venueName + '"' })
    cy.findByLabelText('Lieu').select(offerArchived.venueName)

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: '3 results should be displayed' })
    const expectedResults = [
      ['', '', 'Titre', 'Lieu', 'Établissement', 'Statut'],
      ['', '', offerNotConform.name, offerNotConform.venueName, '', 'non conforme'],
      ['', '', offerInInstruction.name, offerInInstruction.venueName, '', 'en instruction'],
      ['', '', offerArchived.name, offerArchived.venueName, '', 'archivée'],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it(`I should be able to search with a format "${formatName}" and see expected results`, () => {
    cy.stepLog({ message: 'I search with the Format "' + formatName + '"' })
    cy.findByLabelText('Format').select(formatName)

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: '2 results should be displayed' })
    const expectedResults = [
      ['', '', 'Titre', 'Lieu', 'Établissement', 'Statut'],
      ['', '', offerPublished.name, offerPublished.venueName, '', 'publiée'],
      ['', '', offerPublishedTemplate.name, offerPublishedTemplate.venueName, '', 'publiée'],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it(`I should be able to search with a Type "Offre réservable" and see expected results`, () => {
    cy.stepLog({ message: 'I search with the Type "Offre réservable"' })
    cy.findByLabelText('Type de l’offre').select('Offre réservable')

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: '5 results should be displayed' })
    const expectedResults = [
      ['', '', 'Titre', 'Lieu', 'Établissement', 'Statut'],
      ['', '', offerArchived.name, offerArchived.venueName, '', 'archivée'],
      ['', '', offerNotConform.name, offerNotConform.venueName, '', 'non conforme'],
      ['', '', offerInInstruction.name, offerInInstruction.venueName, '', 'en instruction'],
      ['', '', offerDraft.name, offerDraft.venueName, '', 'brouillon'],
      ['', '', offerPublished.name, offerPublished.venueName, '', 'publiée'],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it(`I should be able to search with a Date and see expected results`, () => {
    cy.stepLog({ message: 'I select a date in 2 weeks' })
    const dateSearch = format(addWeeks(new Date(), 2), 'yyyy-MM-dd')
    cy.findByLabelText('Début de la période').type(dateSearch)
    cy.findByLabelText('Fin de la période').type(dateSearch)

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      ['', '', 'Titre', 'Lieu', 'Établissement', 'Statut'],
      ['', '', offerPublished.name, offerPublished.venueName, '', 'publiée'],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it('I should be able to search with a status "En instruction" and see expected results', () => {
    cy.stepLog({ message: 'I search with status "En instruction"' })
    cy.get('#search-status').click()
    cy.get('#list-status').find('#option-display-PENDING').click()
    cy.findByText('Offres collectives').click()

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      ['', '', 'Titre', 'Lieu', 'Établissement', 'Statut'],
      ['', '', offerInInstruction.name, offerInInstruction.venueName, '', 'en instruction'],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it('I should be able to search with several filters and see expected results, then reinit filters', () => {
    cy.stepLog({ message: 'I select ' + offerDraft.venueName + ' in "Lieu"' })
    cy.findByLabelText('Lieu').select(offerDraft.venueName)

    cy.stepLog({ message: 'I select "Représentation" in "Format"' })
    cy.findByLabelText('Format').select('Représentation')

    cy.stepLog({ message: 'I search with the name "brouillon"' })
    cy.findByPlaceholderText('Rechercher par nom d’offre').type('brouillon')

    cy.stepLog({ message: 'I search with status "Brouillon"' })
    cy.get('#search-status').click()
    cy.get('#list-status').find('#option-display-DRAFT').click()
    cy.findByText('Offres collectives').click()

    cy.stepLog({ message: 'I validate my collective filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffers')

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      ['', '', 'Titre', 'Lieu', 'Établissement', 'Statut'],
      ['', '', offerDraft.name, offerDraft.venueName, '', 'brouillon'],
    ]

    expectOffersOrBookingsAreFound(expectedResults)

    cy.stepLog({ message: 'I reset all filters' })
    cy.findByText('Réinitialiser les filtres').click()

    cy.stepLog({ message: 'All filters are empty' })
    cy.findByPlaceholderText('Rechercher par nom d’offre').should('be.empty')
    cy.get('#search-status').should('be.empty')
    cy.findByTestId('wrapper-lieu').within(() => {
      cy.get('select').invoke('val').should('eq', 'all')
    })
    cy.findByTestId('wrapper-format').within(() => {
      cy.get('select').invoke('val').should('eq', 'all')
    })
    cy.findByTestId('wrapper-collectiveOfferType').within(() => {
      cy.get('select').invoke('val').should('eq', 'all')
    })
    cy.findByTestId('wrapper-search-status').within(() => {
      cy.get('select').invoke('val').should('be.empty')
    })

    cy.stepLog({ message: '6 results should be displayed' })
    const expectedResults2 = [
      ['', '', 'Titre', 'Lieu', 'Établissement', 'Statut'],
      ['', '', offerNotConform.name, offerNotConform.venueName, '', 'non conforme'],
      ['', '', offerInInstruction.name, offerInInstruction.venueName, '', 'en instruction'],
      ['', '', offerDraft.name, offerDraft.venueName, '', 'brouillon'],
      ['', '', offerPublished.name, offerPublished.venueName, '', 'publiée'],
      ['', '', offerPublishedTemplate.name, offerPublishedTemplate.venueName, '', 'publiée'],
      ['', '', offerArchived.name, offerArchived.venueName, '', 'archivée'],
    ]

    expectOffersOrBookingsAreFound(expectedResults2)
  })
})
