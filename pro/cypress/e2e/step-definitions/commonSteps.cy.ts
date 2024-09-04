import {
  DataTable,
  Given,
  Then,
  When,
} from '@badeball/cypress-cucumber-preprocessor'

function homePageLoaded(): void {
  cy.findByText('Bienvenue dans l’espace acteurs culturels')
  cy.findByText('Vos adresses')
  cy.findByText('Ajouter un lieu')
  cy.findAllByTestId('spinner').should('not.exist')
}

Given('I open the {string} page', (page: string) => {
  cy.visit('/' + page)
})

Given('I activate a feature flag {string}', (FF: string) => {
  cy.setFeatureFlags([{ name: FF, isActive: true }])
})

When('I go to the {string} page', (page: string) => {
  cy.url().then((urlSource) => {
    cy.findAllByText(page).first().click()
    cy.url().should('not.equal', urlSource)
  })
})

Given('I am logged in with account 1', () => {
  cy.login({
    email: 'retention_structures@example.com',
    password: 'user@AZERTY123',
  })
  homePageLoaded()
})

Given('I am logged in with account 2', () => {
  cy.login({
    email: 'activation@example.com',
    password: 'user@AZERTY123',
  })
  homePageLoaded()
})

Given('I am logged in with account 2 and no cookie selection', () => {
  cy.login({
    email: 'activation@example.com',
    password: 'user@AZERTY123',
    refusePopupCookies: false,
  })
})

// créer un seul scénario createOffers avec son step-def
When('I want to create {string} offer', (offerType: string) => {
  cy.findByText('Au grand public').click()
  cy.findByText(offerType).click()

  cy.intercept({ method: 'GET', url: '/offers/categories' }).as('getCategories')
  cy.findByText('Étape suivante').click()
  cy.wait('@getCategories')
})

When('I select offerer {string}', (offererName: string) => {
  cy.findByTestId('offerer-select').click()
  cy.findByText(/Changer de structure/).click()
  cy.findByTestId('offerers-selection-menu').findByText(offererName).click()
  cy.findByTestId('header-dropdown-menu-div').should('not.exist')
  cy.findAllByTestId('spinner').should('not.exist')
})

Then(
  'These {int} results should be displayed',
  (int: number, dataTable: DataTable) => {
    const numRows = dataTable.rows().length
    const numColumns = dataTable.raw()[0].length
    const data = dataTable.raw()
    const reLAbelCount = new RegExp(
      int + ' ' + '(offre|réservation)' + (int > 1 ? 's' : ''),
      'g'
    )

    cy.findAllByTestId('offer-item-row').should('have.length', numRows)
    cy.contains(reLAbelCount)

    for (let rowLine = 0; rowLine < numRows; rowLine++) {
      const bookLineArray = data[rowLine + 1]

      cy.findAllByTestId('offer-item-row')
        .eq(rowLine)
        .within(() => {
          cy.get('td').then(($elt) => {
            for (let column = 0; column < numColumns; column++) {
              cy.wrap($elt)
                .eq(column)
                .then((cellValue) => {
                  if (cellValue.text().length && bookLineArray[column].length) {
                    return cy.wrap(cellValue).contains(bookLineArray[column])
                  } else {
                    return true
                  }
                })
            }
          })
        })
    }
  }
)

When('I select {string} in {string}', (option: string, filter: string) => {
  cy.findByLabelText(filter).select(option)
})

When('I publish my offer', () => {
  cy.intercept({ method: 'PATCH', url: '/offers/publish', times: 1 }).as(
    'publishOffer'
  )
  cy.intercept({ method: 'GET', url: '/offers/*' }).as('getOffer')
  cy.findByText('Publier l’offre').click()
  cy.wait('@publishOffer', {
    timeout: 60000,
    requestTimeout: 60000,
    responseTimeout: 60000,
  })
  cy.wait('@getOffer', { timeout: 60000 })
})
