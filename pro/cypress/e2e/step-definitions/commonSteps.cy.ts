import {
  DataTable,
  Given,
  Then,
  When,
} from '@badeball/cypress-cucumber-preprocessor'

Given('I open the {string} page', (page: string) => {
  cy.visit('/' + page)
})

When('I go to the {string} page', (page: string) => {
  cy.url().then((urlSource) => {
    cy.findAllByText(page).first().click()
    cy.url().should('not.equal', urlSource)
  })
})

// this account is also in the new interface now
Given('I am logged in', () => {
  cy.login({
    email: 'retention_structures@example.com',
    password: 'user@AZERTY123',
  })
})

Given('I am logged in with the new interface', () => {
  cy.login({
    email: 'activation_new_nav@example.com',
    password: 'user@AZERTY123',
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
  cy.findAllByTestId('spinner').should('not.exist')
})

Then('These results should be displayed', (dataTable: DataTable) => {
  const numRows = dataTable.rows().length
  const numColumns = dataTable.raw()[0].length
  const data = dataTable.raw()
  const reLAbelCount = new RegExp(
    numRows + ' ' + '(offre|réservation)' + (numRows > 1 ? 's' : ''),
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
})
