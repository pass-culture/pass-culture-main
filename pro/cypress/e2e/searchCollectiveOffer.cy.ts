import {
  expectOffersOrBookingsAreFound,
  logAndGoToPage,
} from '../support/helpers.ts'

describe('Search collective offers', () => {
  let login: string
  const venueName = 'Mon Lieu'
  const offerName = 'Mon offre collective'

  before(() => {
    cy.visit('/connexion')
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_pro_user_with_collective_offers',
    }).then((response) => {
      login = response.body.user.email
    })
    cy.intercept({ method: 'GET', url: '/collective/offers*' }).as(
      'collectiveOffers'
    )
  })

  it('I should be able to search with several filters and see expected results', () => {
    logAndGoToPage(login, '/offres/collectives')
    cy.wait('@collectiveOffers')

    cy.stepLog({ message: 'I select "Mon Lieu" in "Lieu"' })
    cy.findByLabelText('Lieu').select(venueName)

    cy.stepLog({ message: 'I select "Projection audiovisuelle" in "Format"' })
    cy.findByLabelText('Format').select('Projection audiovisuelle')

    cy.stepLog({ message: 'I validate my collective filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffers')

    cy.stepLog({ message: '1 result should be displayed' })
    const expectedResults = [
      ['', '', 'Titre', 'Lieu', 'Établissement', 'Status'],
      ['', '', offerName, venueName, 'Tous les établissements', 'publiée'],
    ]

    cy.findAllByTestId('offer-item-row').should('have.length', 1)

    expectOffersOrBookingsAreFound(expectedResults)
  })
})
