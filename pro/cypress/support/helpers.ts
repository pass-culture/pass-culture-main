import {
  MOCKED_BACK_ADDRESS_LABEL,
  MOCKED_BACK_ADDRESS_STREET,
} from '../support/constants.ts'

/**
 * This function takes a string[][] as a DataTable representing the data
 * in a Table and checks that what is displayed is what is expected.
 * Also checks that the label above is counting the right number of rows: `3 offres`.
 * First row represents the title of columns and is not checked
 *
 * @export
 * @param {Array<Array<string>>} expectedResults
 * @example 
 * const expectedResults = [
      ['Réservation', "Nom de l'offre", 'Établissement', 'Places et prix', 'Statut'],
      ['1', 'Mon offre', 'COLLEGE DE LA TOUR', '25 places', 'confirmée'],
    ]
   expectOffersOrBookingsAreFound(expectedResults)
 */
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
                if (lineArray[column].length) {
                  let isAMatch: boolean = cellValue.text().includes(lineArray[column])
                  expect(isAMatch).to.be.true
                }
              })
          }
        })
      })
  }
}

/**
 * Login then go to a page. This function does not use `session()` so browser
 * session will not be restored when reused in a test unlike the
 * `sessionLogInAndGoToPage()`function
 *
 * @param {string} login email to use for login (password used is a default one)
 * @param {string} path path to the page that will be visited after login
 * @param {boolean} [setDefaultCookieOrejime=true] optional param: close the
 * cookie popup in all pages (default is true)
 */
export function logInAndGoToPage(
  login: string,
  path: string,
  setDefaultCookieOrejime: boolean = true
) {
  const password = 'user@AZERTY123'
  cy.stepLog({ message: `I am logged in with account ${login}` })
  cy.intercept({ method: 'POST', url: '/users/signin' }).as('signinUser')
  cy.intercept({ method: 'GET', url: '/offerers/names' }).as('offererNames')

  cy.visit('/connexion')
  if (setDefaultCookieOrejime) {
    cy.setCookie(
      'orejime',
      '{"firebase":true,"hotjar":true,"beamer":true,"sentry":true}'
    )
  }

  cy.get('#email').type(login)
  cy.get('#password').type(password)
  cy.get('button[type=submit]').click()
  cy.wait(['@signinUser', '@offererNames'])

  cy.stepLog({ message: `I open the "${path}" page` })
  cy.visit(path)
  if (path === '/accueil') {
    homePageLoaded()
  } else {
    cy.url().should('contain', path)
    cy.findAllByTestId('spinner').should('not.exist')
  }
}

/**
 * Same as `logInAndGoToPage` but encapsulated in a `session()` in order
 * to be able to reuse the browser session, then the connexion and data
 * created with Factory routes
 *
 * @param {string} sessionName name of the session. Same name will reuse browser session
 * @param {string} login email to use for login (password used is a default one)
 * @param {string} path path to the page that will be visited after login
 */
export function sessionLogInAndGoToPage(
  sessionName: string,
  login: string,
  path: string
) {
  cy.session(sessionName, () => {
    logInAndGoToPage(login, path)
  })
  cy.visit(path)
}


/**
 * Checks that the homepage is loaded and displayed
 *
 */
export function homePageLoaded() {
  cy.findByText('Bienvenue dans l’espace acteurs culturels')
  cy.findByText('Vos adresses')
  cy.findByText('Ajouter un lieu')
  cy.findAllByTestId('spinner').should('not.exist')
}

/**
 * Intercept and stub a response with an alias `.as('search5Address')`

 * @see https://docs.cypress.io/api/commands/intercept#Dynamically-stubbing-a-response
 * @example
 * interceptSearch5Adresses()
 * ...
 * cy.wait('@search5Address')
 */
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
