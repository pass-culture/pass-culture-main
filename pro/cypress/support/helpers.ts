import {
  MOCKED_BACK_ADDRESS_LABEL,
  MOCKED_BACK_ADDRESS_STREET,
} from '../support/constants.ts'

export function expectOffersOrBookingsAreFound(
  expectedResults: Array<Array<string>>
) {
  const expectedLength = expectedResults.length - 1
  const regexExpectedCount = new RegExp(
    expectedLength +
      ' ' +
      '(offre|réservation)' +
      (expectedLength > 1 ? 's' : ''),
    'g'
  )

  cy.contains(regexExpectedCount)

  cy.findAllByTestId('offer-item-row').should('have.length', expectedLength)

  for (let rowLine = 0; rowLine < expectedLength; rowLine++) {
    const lineArray = expectedResults[rowLine + 1]

    cy.findAllByTestId('offer-item-row')
      .eq(rowLine)
      .within(() => {
        cy.get('td').then(($elt) => {
          for (let column = 0; column < lineArray.length; column++) {
            cy.wrap($elt)
              .eq(column)
              .then((cellValue) => {
                if (cellValue.text().length && lineArray[column].length) {
                  return cy
                    .wrap(cellValue)
                    .should('contain.text', lineArray[column])
                } else {
                  return true
                }
              })
          }
        })
      })
  }
}

export function logInAndGoToPage(
  login: string,
  url: string,
  setDefaultCookieOrejime = true
) {
  const password = 'user@AZERTY123'
  cy.stepLog({ message: `I am logged in with account ${login}` })
  cy.intercept({ method: 'POST', url: '/users/signin' }).as('signinUser')
  cy.intercept({ method: 'GET', url: '/offerers/names' }).as('offererNames')

  cy.visit('/connexion')
  if (setDefaultCookieOrejime)
    {cy.setCookie('orejime','{"firebase":true,"hotjar":true,"beamer":true,"sentry":true}')}

  cy.get('#email').type(login)
  cy.get('#password').type(password)
  cy.get('button[type=submit]').click()
  cy.wait(['@signinUser', '@offererNames'])

  cy.stepLog({ message: `I open the "${url}" page` })
  cy.visit(url)
  if (url === '/accueil') {
    homePageLoaded()
  } else {
    cy.url().should('contain', url)
    cy.findAllByTestId('spinner').should('not.exist')
  }
}

export function sessionLogInAndGoToPage(
  sessionName: string,
  login: string,
  url: string
) {
  cy.session(sessionName, () => {
    logInAndGoToPage(login, url)
  })
  cy.visit(url)
}

export function homePageLoaded() {
  cy.findByText('Bienvenue dans l’espace acteurs culturels')
  cy.findByText('Vos adresses')
  cy.findByText('Ajouter un lieu')
  cy.findAllByTestId('spinner').should('not.exist')
}

export function interceptSearch5Adresses() {
  cy.intercept(
    'GET',
    'https://api-adresse.data.gouv.fr/search/?limit=5&q=*',
    (req) =>
      req.reply({
        statusCode: 200,
        body: {
          type: 'FeatureCollection',
          version: 'draft',
          features: [
            {
              type: 'Feature',
              geometry: { type: 'Point', coordinates: [2.3056966, 48.8716934] },
              properties: {
                label: MOCKED_BACK_ADDRESS_LABEL,
                score: 0.97351,
                housenumber: '89',
                id: '75108_5194_00089',
                name: MOCKED_BACK_ADDRESS_STREET,
                postcode: '75008',
                citycode: '75108',
                x: 649261.94,
                y: 6863742.69,
                city: 'Paris',
                district: 'Paris 8e Arrondissement',
                context: '75, Paris, Île-de-France',
                type: 'housenumber',
                importance: 0.70861,
                street: MOCKED_BACK_ADDRESS_STREET,
              },
            },
          ],
          attribution: 'BAN',
          licence: 'ETALAB-2.0',
          query: MOCKED_BACK_ADDRESS_LABEL,
          limit: 5,
        },
      })
  ).as('search5Address')
}
