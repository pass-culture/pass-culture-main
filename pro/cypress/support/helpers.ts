import {
  DEFAULT_AXE_RULES,
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
                  expect(cellValue.text()).to.include(lineArray[column])
                }
              })
          }
        })
      })
  }
}

/**
 * Login
 *
 * @param {string} login email to use for login (password used is a default one)
 * @param {boolean} [setDefaultCookieOrejime=true] optional param: close the
 * cookie popup in all pages (default is true)
 */
function doLogin(
  login: string,
  setDefaultCookieOrejime: boolean = true,
  retry: boolean = true
): Cypress.Chainable {
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

  // Sometimes, the page is loaded with the input disabled
  cy.get('#email').should('be.enabled')
  cy.get('#email').type(login)
  cy.get('#password').type(password)
  cy.get('button[type=submit]').click()

  return cy.wait('@signinUser').then(({ response }) => {
    if (response?.statusCode !== 200 && retry) {
      // eslint-disable-next-line cypress/no-unnecessary-waiting
      return cy.wait(5000).then(() => {
        return doLogin(login, setDefaultCookieOrejime, false)
      })
    }
    cy.wait('@offererNames')
  })
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
  doLogin(login, setDefaultCookieOrejime).then(() => {
    cy.stepLog({ message: `I open the "${path}" page` })
    cy.visit(path)
    if (path === '/accueil') {
      homePageLoaded()
    } else {
      cy.url().should('contain', path)
      cy.findAllByTestId('spinner').should('not.exist')
    }
  })
}

/**
 * Logs in with the provided email and navigates to the didactic onboarding page.
 * Optionally sets the default cookie to close the cookie popup on all pages.
 *
 * @param {string} login - The email to use for login (password used is a default one).
 * @param {boolean} [setDefaultCookieOrejime=true] - Optional parameter to close the cookie popup on all pages (default is true).
 */
export function logInAndSeeDidacticOnboarding(
  login: string,
  setDefaultCookieOrejime = true
) {
  doLogin(login, setDefaultCookieOrejime).then(() => {
    cy.stepLog({ message: `I open the /onboarding page` })
    cy.visit('/onboarding')

    cy.findAllByTestId('spinner').should('not.exist')

    cy.findByText('Bienvenue sur le pass Culture Pro !')
    cy.findByText('À qui souhaitez-vous proposer votre première offre ?')
    cy.findByText('Aux jeunes sur l’application mobile pass Culture')
    cy.findByText('Aux enseignants sur la plateforme ADAGE')
    cy.findAllByText('Commencer').should('have.length', 2)
  })
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
  cy.findByText('Bienvenue sur votre espace partenaire')
  cy.findAllByText(/Votre page partenaire|Vos pages partenaire/)
  cy.findAllByTestId('spinner').should('not.exist')
  cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
}

/**
 * Intercept and stub a response with an alias `.as('search5Address')`

 * @see https://docs.cypress.io/api/commands/intercept#Dynamically-stubbing-a-response
 * @example
 * interceptSearch5Adresses()
 * ...
 * cy.wait('@search5Address')
 * FIXME 22/04/25 bdalbianco: change this and constants.ts to reproduce proper api address call 
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

export function collectiveFormatEventDate(date: string) {
  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: 'Europe/Paris',
  })
    .format(new Date(date))
    .replace(/[,:]/g, 'h')
    .replace(' ', '')
}
