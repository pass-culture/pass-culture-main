import { When, Then, DataTable } from '@badeball/cypress-cucumber-preprocessor'

When('I search with the text {string}', (title: string) => {
  cy.findByPlaceholderText('Rechercher par nom d’offre ou par EAN-13').type(
    title
  )
  cy.findByText('Rechercher').click()
})

Then('These results should be displayed', (dataTable: DataTable) => {
  const numRows = dataTable.rows().length
  cy.findAllByTestId('offer-item-row').should('have.length', numRows)
  cy.contains(numRows + ' offre' + (numRows > 1 ? 's' : ''))

  const data = dataTable.raw()

  for (var rowLine = 0; rowLine < numRows; rowLine++) {
    const bookLineArray = data[rowLine + 1]

    cy.findAllByTestId('offer-item-row')
      .eq(rowLine)
      .within(() => {
        cy.get('td').then(($elt) => {
          // Check title
          cy.wrap($elt).eq(2).should('contain', bookLineArray[0])
          // Check venue
          cy.wrap($elt).eq(3).should('contain', bookLineArray[1])
          // Check Stock
          cy.wrap($elt).eq(4).should('contain', bookLineArray[2])
          // Check Status
          cy.wrap($elt).eq(5).should('contain', bookLineArray[3])
        })
      })
  }
})
