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

export function logAndGoToPage(login: string, url: string) {
  const password = 'user@AZERTY123'

  cy.stepLog({ message: 'I am logged in' })
  cy.login({
    email: login,
    password: password,
    redirectUrl: '/',
  })
  cy.findAllByTestId('spinner').should('not.exist')

  cy.stepLog({ message: `I open the "${url}" page` })
  cy.visit(url)
  cy.findAllByTestId('spinner').should('not.exist')

  if (url === '/accueil') {
    homePageLoaded()
  }
}

export function homePageLoaded() {
  cy.findByText('Bienvenue dans l’espace acteurs culturels')
  cy.findByText('Vos adresses')
  cy.findByText('Ajouter un lieu')
  cy.findAllByTestId('spinner').should('not.exist')
}
