import { addWeeks, format } from 'date-fns'

import {
  BOOKABLE_OFFERS_COLUMNS,
  DEFAULT_AXE_CONFIG,
  DEFAULT_AXE_RULES,
} from '../support/constants.ts'
import {
  collectiveFormatEventDate,
  expectOffersOrBookingsAreFound,
  logInAndGoToPage,
} from '../support/helpers.ts'

const institutionName = 'COLLEGE 123'

describe('Search collective offers', () => {
  let offerPublished: {
    name: string
    venueName: string
    startDatetime: string
    endDatetime: string
  }
  let offerArchived: { name: string; venueName: string }
  let offerDraft: { name: string; venueName: string }

  const formatName = 'Concert'

  beforeEach(() => {
    cy.intercept({ method: 'GET', url: '/collective/bookable-offers*' }).as(
      'collectiveOffersBookable'
    )
    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_pro_user_with_collective_offers',
      (response) => {
        logInAndGoToPage(response.body.user.email, '/accueil')
        offerPublished = response.body.offerPublished
        offerArchived = response.body.offerArchived
        offerDraft = response.body.offerDraft
        cy.visit('/offres/collectives')
        cy.wait(['@collectiveOffersBookable'])
        cy.findAllByTestId('spinner').should('not.exist')
      }
    )
  })

  it(`I should be able to search with a name and see expected results`, () => {
    cy.stepLog({
      message: `I search with the name "${offerPublished.name}"`,
    })

    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)

    cy.findByLabelText(/Nom de l’offre/).type(offerPublished.name)
    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffersBookable')
      .its('response.statusCode')
      .should('eq', 200)

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        offerPublished.name,
        `Du ${collectiveFormatEventDate(offerPublished.startDatetime)}au ${collectiveFormatEventDate(offerPublished.endDatetime)}`,
        '100€25 participants',
        institutionName,
        'À déterminer',
        'publiée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it(`I should be able to search with a location and see expected results`, () => {
    cy.stepLog({ message: 'I open the filters' })
    cy.findByText('Filtrer').click()

    cy.stepLog({
      message: `I search with the place "En établissement scolaire"`,
    })
    cy.findByLabelText('Localisation').select('En établissement scolaire')

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffersBookable')
      .its('response.statusCode')
      .should('eq', 200)

    cy.stepLog({ message: '1 results should be displayed' })
    const expectedResults = [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        offerArchived.name,
        '-',
        '-',
        'DE LA TOUR',
        "Dans l'établissement",
        'archivée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it(`I should be able to search with a format "${formatName}" and see expected results`, () => {
    cy.stepLog({ message: 'I open the filters' })
    cy.findByText('Filtrer').click()

    cy.stepLog({ message: `I search with the Format "${formatName}"` })
    cy.findByLabelText('Format').select(formatName)

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffersBookable')
      .its('response.statusCode')
      .should('eq', 200)

    cy.stepLog({ message: '1 results should be displayed' })
    const expectedResults = [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        offerPublished.name,
        `Du ${collectiveFormatEventDate(offerPublished.startDatetime)}au ${collectiveFormatEventDate(offerPublished.endDatetime)}`,
        '100€25 participants',
        institutionName,
        'À déterminer',
        'publiée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it(`I should be able to search with a Date and see expected results`, () => {
    cy.stepLog({ message: 'I open the filters' })
    cy.findByText('Filtrer').click()

    cy.stepLog({ message: 'I select a date in 2 weeks' })
    const dateSearch = format(addWeeks(new Date(), 2), 'yyyy-MM-dd')
    cy.findByLabelText('Début de la période').type(dateSearch)
    cy.findByLabelText('Fin de la période').type(dateSearch)

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffersBookable')
      .its('response.statusCode')
      .should('eq', 200)

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        offerPublished.name,
        `Du ${collectiveFormatEventDate(offerPublished.startDatetime)}au ${collectiveFormatEventDate(offerPublished.endDatetime)}`,
        '100€25 participants',
        institutionName,
        'À déterminer',
        'publiée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it('I should be able to search with a status "Publiée" and see expected results', () => {
    cy.stepLog({ message: 'I open the filters' })
    cy.findByText('Filtrer').click()

    cy.stepLog({ message: 'I search with status "Publiée sur ADAGE"' })
    cy.findByRole('button', { name: 'Statut' }).click()
    cy.findByText('Publiée sur ADAGE').click()
    // We click outside the filter to close it
    cy.findByRole('heading', { name: 'Offres réservables' }).click()

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffersBookable')
      .its('response.statusCode')
      .should('eq', 200)

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        offerPublished.name,
        `Du ${collectiveFormatEventDate(offerPublished.startDatetime)}au ${collectiveFormatEventDate(offerPublished.endDatetime)}`,
        '100€25 participants',
        institutionName,
        'À déterminer',
        'publiée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it('I should be able to search with several filters and see expected results, then reinit filters', () => {
    cy.stepLog({ message: 'I open the filters' })
    cy.findByText('Filtrer').click()

    cy.stepLog({
      message: 'I select "À déterminer" in "Localisation"',
    })
    cy.findByLabelText('Localisation').select('À déterminer')

    cy.stepLog({ message: 'I select "Représentation" in "Format"' })
    cy.findByLabelText('Format').select('Représentation')

    cy.stepLog({ message: 'I search with the name "brouillon"' })
    cy.findByLabelText(/Nom de l’offre/).type('brouillon', { delay: 0 })

    cy.stepLog({ message: 'I search with status "Brouillon"' })
    cy.findByRole('button', { name: 'Statut' }).click()
    cy.findByTestId('panel-scrollable').scrollTo('bottom')
    cy.findByText('Brouillon').click()
    // We click outside the filter to close it
    cy.findByRole('heading', { name: 'Offres réservables' }).click()

    cy.stepLog({ message: 'I validate my collective filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffersBookable')

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        offerDraft.name,
        '-',
        '-',
        'DE LA TOUR',
        'À déterminer',
        'brouillon',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)

    cy.stepLog({ message: 'I reset all filters' })
    cy.findByText('Réinitialiser les filtres').click()

    cy.stepLog({ message: 'All filters are empty' })
    cy.findByRole('button', { name: 'Statut' }).click()

    cy.findByText('En instruction').should('not.be.checked')

    cy.findByRole('combobox', { name: /Localisation/ })
      .invoke('val')
      .should('eq', 'all')

    cy.findByRole('combobox', { name: /Format/ })
      .invoke('val')
      .should('eq', 'all')

    cy.stepLog({ message: 'I reset the name search' })
    cy.findByLabelText(/Nom de l’offre/).clear()

    cy.stepLog({ message: 'I make a new search' })
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffersBookable')

    cy.stepLog({ message: '5 results should be displayed' })
    cy.contains('5 offres')
  })

  it('I should be able to download offers in CSV and Excel format', () => {
    cy.stepLog({ message: 'I open the download drawer' })
    cy.findByText('Télécharger').click()

    cy.stepLog({ message: 'I download CSV format' })
    cy.intercept('GET', '/collective/offers/csv*').as('downloadCSV')
    cy.findByText('Télécharger format CSV').click()
    cy.wait('@downloadCSV').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'I download Excel format' })
    cy.intercept('GET', '/collective/offers/excel*').as('downloadExcel')
    cy.findByText('Télécharger format Excel').click()
    cy.wait('@downloadExcel').its('response.statusCode').should('eq', 200)
  })
})
