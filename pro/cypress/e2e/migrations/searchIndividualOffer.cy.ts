import { addDays, format } from 'date-fns'

function expectOffersAreFound(expectedResults: Array<Array<string>>) {
  for (let rowLine = 0; rowLine < expectedResults.length - 1; rowLine++) {
    const offerLineArray = expectedResults[rowLine + 1]

    cy.findAllByTestId('offer-item-row')
      .eq(rowLine)
      .within(() => {
        cy.get('td').then(($elt) => {
          for (let column = 0; column < 6; column++) {
            cy.wrap($elt)
              .eq(column)
              .then((cellValue) => {
                if (cellValue.text().length && offerLineArray[column].length) {
                  return cy
                    .wrap(cellValue)
                    .should('contain.text', offerLineArray[column])
                } else {
                  return true
                }
              })
          }
        })
      })
  }
}

describe('Search individual offers', () => {
  let login: string
  const password = 'user@AZERTY123'
  const venueName = 'Mon Lieu'
  const offerName1 = 'Une super offre'
  const offerName2 = 'Une offre avec ean'
  const offerName3 = 'Une flûte traversière'
  const offerName4 = "Un concert d'electro inoubliable"
  const offerName5 = 'Une autre offre incroyable'
  const offerName6 = 'Encore une offre incroyable'
  const offerName7 = 'Une offre épuisée'

  beforeEach(() => {
    cy.visit('/connexion')
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_pro_user_with_individual_offers',
    }).then((response) => {
      login = response.body.user.email
    })
    cy.intercept({
      method: 'GET',
      url: '/offers?**',
    }).as('searchOffers')
  })

  it('A search with a name should display expected results', () => {
    cy.stepLog({ message: 'I am logged in' })
    cy.login({
      email: login,
      password: password,
      redirectUrl: '/',
    })
    cy.url().then((urlSource) => {
      cy.findAllByText('Offres').first().click()
      cy.url().should('not.equal', urlSource)
    })
    cy.findAllByTestId('spinner').should('not.exist')

    cy.stepLog({ message: 'I search with the text "Une super offre"' })
    cy.findByPlaceholderText('Rechercher par nom d’offre ou par EAN-13').type(
      offerName1
    )

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'These results should be displayed' })
    const expectedResults = [
      ['', '', 'Titre', 'Lieu', 'Stocks', 'Status'],
      ['', '', offerName1, venueName, '1 000', 'publiée'],
    ]

    cy.findAllByTestId('offer-item-row').should('have.length', 1)
    cy.contains('1 offre')

    expectOffersAreFound(expectedResults)
  })

  it('A search with a EAN should display expected results', () => {
    const ean = '1234567891234'

    cy.stepLog({ message: 'I am logged in' })
    cy.login({
      email: login,
      password: password,
      redirectUrl: '/',
    })
    cy.url().then((urlSource) => {
      cy.findAllByText('Offres').first().click()
      cy.url().should('not.equal', urlSource)
    })
    cy.findAllByTestId('spinner').should('not.exist')

    cy.stepLog({ message: 'I search with the text:' + ean })
    cy.findByPlaceholderText('Rechercher par nom d’offre ou par EAN-13').type(
      ean
    )

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'These results should be displayed' })
    const expectedResults = [
      ['', '', 'Titre', 'Lieu', 'Stocks', 'Status'],
      ['', '', offerName2 + ean, venueName, '1 000', 'publiée'],
    ]

    cy.findAllByTestId('offer-item-row').should('have.length', 1)
    cy.contains('1 offre')

    expectOffersAreFound(expectedResults)
  })

  it('A search with "Catégories" filter should display expected results', () => {
    cy.stepLog({ message: 'I am logged in' })
    cy.login({
      email: login,
      password: password,
      redirectUrl: '/',
    })
    cy.url().then((urlSource) => {
      cy.findAllByText('Offres').first().click()
      cy.url().should('not.equal', urlSource)
    })
    cy.findAllByTestId('spinner').should('not.exist')

    cy.stepLog({ message: 'I select "Instrument de musique" in "Catégories"' })
    cy.findByLabelText('Catégories').select('Instrument de musique')

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'These results should be displayed' })
    const expectedResults = [
      ['', '', 'Titre', 'Lieu', 'Stocks', 'Status'],
      ['', '', offerName3, venueName, '1 000', 'publiée'],
    ]

    cy.findAllByTestId('offer-item-row').should('have.length', 1)
    cy.contains('1 offre')

    expectOffersAreFound(expectedResults)
  })

  it('A search by offer status should display expected results', () => {
    cy.stepLog({ message: 'I am logged in' })
    cy.login({
      email: login,
      password: password,
      redirectUrl: '/',
    })
    cy.url().then((urlSource) => {
      cy.findAllByText('Offres').first().click()
      cy.url().should('not.equal', urlSource)
    })
    cy.findAllByTestId('spinner').should('not.exist')

    cy.stepLog({ message: 'I select "Publiée" in offer status' })
    cy.findByTestId('wrapper-status').within(() => {
      cy.get('select').select('Publiée')
    })

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'These results should be displayed' })
    const expectedResults = [
      ['', '', 'Titre', 'Lieu', 'Stocks', 'Status'],
      ['', '', offerName6, venueName, '1 000', 'publiée'],
      ['', '', offerName5, venueName, '1 000', 'publiée'],
      ['', '', offerName4, venueName, '1 000', 'publiée'],
      ['', '', offerName3, venueName, '1 000', 'publiée'],
      ['', '', offerName2, venueName, '1 000', 'publiée'],
      ['', '', offerName1, venueName, '1 000', 'publiée'],
    ]

    cy.findAllByTestId('offer-item-row').should('have.length', 6)
    cy.contains('6 offres')

    expectOffersAreFound(expectedResults)
  })

  it('A search by date should display expected results', () => {
    cy.stepLog({ message: 'I am logged in' })
    cy.login({
      email: login,
      password: password,
      redirectUrl: '/',
    })
    cy.url().then((urlSource) => {
      cy.findAllByText('Offres').first().click()
      cy.url().should('not.equal', urlSource)
    })
    cy.findAllByTestId('spinner').should('not.exist')

    cy.stepLog({ message: 'I select a date in one month' })
    const dateSearch = format(addDays(new Date(), 30), 'yyyy-MM-dd')
    cy.findByLabelText('Début de la période').type(dateSearch)
    cy.findByLabelText('Fin de la période').type(dateSearch)

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'These results should be displayed' })
    const expectedResults = [
      ['', '', 'Titre', 'Lieu', 'Stocks', 'Status'],
      ['', '', offerName4, venueName, '1 000', 'publiée'],
    ]

    cy.findAllByTestId('offer-item-row').should('have.length', 1)
    cy.contains('1 offre')

    expectOffersAreFound(expectedResults)
  })

  it('A search combining several filters should display expected results', () => {
    cy.stepLog({ message: 'I am logged in' })
    cy.login({
      email: login,
      password: password,
      redirectUrl: '/',
    })
    cy.url().then((urlSource) => {
      cy.findAllByText('Offres').first().click()
      cy.url().should('not.equal', urlSource)
    })

    cy.findAllByTestId('spinner').should('not.exist')

    cy.stepLog({ message: 'I search with the text "Livre"' })
    cy.findByPlaceholderText('Rechercher par nom d’offre ou par EAN-13').type(
      'incroyable'
    )

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'I select "Livre" in "Catégories"' })
    cy.findByLabelText('Catégories').select('Livre')

    cy.stepLog({ message: 'I select "Librairie 10" in "Lieu"' })
    cy.findByLabelText('Lieu').select(venueName)

    cy.stepLog({ message: 'I select "Publiée" in offer status' })
    cy.findByTestId('wrapper-status').within(() => {
      cy.get('select').select('Publiée')
    })

    cy.stepLog({ message: 'I validate my filters' })
    cy.findByText('Rechercher').click()
    cy.wait('@searchOffers').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'These 2 results should be displayed' })
    const expectedResults = [
      ['', '', 'Titre', 'Lieu', 'Stocks', 'Status'],
      ['', '', offerName6, venueName, '1 000', 'publiée'],
      ['', '', offerName5, venueName, '1 000', 'publiée'],
    ]

    cy.findAllByTestId('offer-item-row').should('have.length', 2)
    cy.contains('2 offres')

    expectOffersAreFound(expectedResults)

    cy.stepLog({ message: 'I reset all filters' })
    cy.findByText('Réinitialiser les filtres').click()

    cy.stepLog({ message: 'All filters are empty' })
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

    cy.stepLog({ message: 'These results should be displayed' })
    const expectedResults2 = [
      ['', '', 'Titre', 'Lieu', 'Stocks', 'Status'],
      ['', '', offerName7, venueName, '0', 'épuisée'],
      ['', '', offerName6, venueName, '1 000', 'publiée'],
      ['', '', offerName5, venueName, '1 000', 'publiée'],
      ['', '', offerName4, venueName, '1 000', 'publiée'],
      ['', '', offerName3, venueName, '1 000', 'publiée'],
      ['', '', offerName2, venueName, '1 000', 'publiée'],
      ['', '', offerName1, venueName, '1 000', 'publiée'],
    ]

    cy.findAllByTestId('offer-item-row').should('have.length', 7)
    cy.contains('7 offres')

    expectOffersAreFound(expectedResults2)
  })
})
