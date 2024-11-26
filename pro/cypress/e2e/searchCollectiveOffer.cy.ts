import { addWeeks, format } from 'date-fns'

import {
  expectOffersOrBookingsAreFound,
  logAndGoToPage,
} from '../support/helpers.ts'

describe('Search collective offers', () => {
  let login: string
  const venueName1 = 'Mon Lieu 1'
  const venueName2 = 'Mon Lieu 2'
  const offerNameArchived = 'Mon offre collective archivée réservable'
  const offerNamePublished = 'Mon offre collective publiée réservable'
  const offerNamePublishedTemplate = 'Mon offre collective publiée vitrine'
  const offerNameDraft = 'Mon offre collective en brouillon réservable'
  const offerNameNotConform = 'Mon offre collective non conforme réservable'
  const offerNameInInstruction = 'Mon offre collective en instruction réservable'
  const formatName = 'Concert'

  before(() => {
    cy.visit('/connexion')
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_pro_user_with_collective_offers',
    }).then((response) => {
      login = response.body.user.email
    })
    cy.setFeatureFlags([
      { name: 'ENABLE_COLLECTIVE_NEW_STATUSES', isActive: true },
    ])
  })

  beforeEach(() => {
    logAndGoToPage(login, '/accueil')

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

  it(`I should be able to search with a name "${offerNamePublished}" and see expected results`, () => {
    cy.stepLog({
      message: 'I search with the name "' + offerNamePublished + '"',
    })
    cy.findByPlaceholderText('Rechercher par nom d’offre').type(
      offerNamePublished
    )

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      ['', '', 'Titre', 'Lieu', 'Établissement', 'Statut'],
      [
        '',
        '',
        offerNamePublished,
        venueName1,
        'Tous les établissements',
        'publiée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it(`I should be able to search with a lieu "${venueName2}" and see expected results`, () => {
    cy.stepLog({ message: 'I search with the place "' + venueName2 + '"' })
    cy.findByLabelText('Lieu').select(venueName2)

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: '3 results should be displayed' })
    const expectedResults = [
      ['', '', 'Titre', 'Lieu', 'Établissement', 'Statut'],
      [
        '',
        '',
        offerNameNotConform,
        venueName2,
        'Tous les établissements',
        'non conforme',
      ],
      [
        '',
        '',
        offerNameInInstruction,
        venueName2,
        'Tous les établissements',
        'en instruction',
      ],
      [
        '',
        '',
        offerNameArchived,
        venueName2,
        'Tous les établissements',
        'archivée',
      ],
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
      [
        '',
        '',
        offerNamePublished,
        venueName1,
        'Tous les établissements',
        'publiée',
      ],
      [
        '',
        '',
        offerNamePublishedTemplate,
        venueName1,
        'Tous les établissements',
        'publiée',
      ],
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
      [
        '',
        '',
        offerNameArchived,
        venueName2,
        'Tous les établissements',
        'archivée',
      ],
      [
        '',
        '',
        offerNameNotConform,
        venueName2,
        'Tous les établissements',
        'non conforme',
      ],
      [
        '',
        '',
        offerNameInInstruction,
        venueName2,
        'Tous les établissements',
        'en instruction',
      ],
      [
        '',
        '',
        offerNameDraft,
        venueName1,
        'Tous les établissements',
        'brouillon',
      ],
      [
        '',
        '',
        offerNamePublished,
        venueName1,
        'Tous les établissements',
        'publiée',
      ],
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
      [
        '',
        '',
        offerNamePublished,
        venueName1,
        'Tous les établissements',
        'publiée',
      ],
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
      [
        '',
        '',
        offerNameInInstruction,
        venueName2,
        'Tous les établissements',
        'en instruction',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults)
  })

  it('I should be able to search with several filters and see expected results, then reinit filters', () => {
    cy.stepLog({ message: 'I select ' + venueName1 + ' in "Lieu"' })
    cy.findByLabelText('Lieu').select(venueName1)

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
      [
        '',
        '',
        offerNameDraft,
        venueName1,
        'Tous les établissements',
        'brouillon',
      ],
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
      [
        '',
        '',
        offerNameNotConform,
        venueName2,
        'Tous les établissements',
        'non conforme',
      ],
      [
        '',
        '',
        offerNameInInstruction,
        venueName2,
        'Tous les établissements',
        'en instruction',
      ],
      [
        '',
        '',
        offerNameDraft,
        venueName1,
        'Tous les établissements',
        'brouillon',
      ],
      [
        '',
        '',
        offerNamePublished,
        venueName1,
        'Tous les établissements',
        'publiée',
      ],
      [
        '',
        '',
        offerNamePublishedTemplate,
        venueName1,
        'Tous les établissements',
        'publiée',
      ],
      [
        '',
        '',
        offerNameArchived,
        venueName2,
        'Tous les établissements',
        'archivée',
      ],
    ]

    expectOffersOrBookingsAreFound(expectedResults2)
  })
})
