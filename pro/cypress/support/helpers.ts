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
