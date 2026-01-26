import { expect, type Page } from '@playwright/test'

export async function expectSuccessSnackbar(
  page: Page,
  message: string
): Promise<void> {
  await expect(
    page
      .locator('[data-testid^="global-snack-bar-success"]')
      .filter({ hasText: message })
  ).toBeVisible()
}

/**
 * This function takes a string[][] as a DataTable representing the data
 * in a Table and checks that what is displayed is what is expected.
 * Also checks that the label above is counting the right number of rows: `3 offres`.
 * First row represents the title of columns and is not checked
 *
 * @param {Page} page
 * @param {Array<Array<string>>} expectedResults
 * @param {string} countLabel - The label pattern to match (e.g., 'offre', '(offre|réservation)')
 * @example
 * const expectedResults = [
      ['Réservation', "Nom de l'offre", 'Établissement', 'Places et prix', 'Statut'],
      ['1', 'Mon offre', 'COLLEGE DE LA TOUR', '25 places', 'confirmée'],
    ]
   await expectOffersOrBookingsAreFound(page, expectedResults, '(offre|réservation)')
 */
async function expectOffersOrBookingsAreFound(
  page: Page,
  expectedResults: Array<Array<string>>,
  countLabel: string
): Promise<void> {
  const expectedLength = expectedResults.length - 1
  const regexExpectedCount = new RegExp(
    expectedLength + ' ' + countLabel + (expectedLength > 1 ? 's' : ''),
    'g'
  )

  await expect(page.getByText(regexExpectedCount).first()).toBeVisible()

  const rows = page.locator('tbody').locator('tr[data-testid="table-row"]')
  await expect(rows).toHaveCount(expectedLength)

  for (let rowLine = 0; rowLine < expectedLength; rowLine++) {
    const lineArray = expectedResults[rowLine + 1]
    const row = rows.nth(rowLine)
    const cells = row.locator('td')

    for (let column = 0; column < lineArray.length; column++) {
      if (lineArray[column].length) {
        await expect(cells.nth(column)).toContainText(lineArray[column])
      }
    }
  }
}

/**
 * This function takes a string[][] as a DataTable representing the data
 * in a Table and checks that what is displayed is what is expected.
 * Also checks that the label above is counting the right number of rows: `3 offres`.
 * First row represents the title of columns and is not checked
 *
 * @export
 * @param {Page} page
 * @param {Array<Array<string>>} expectedResults
 * @example
 * const expectedResults = [
      ['Réservation', "Nom de l'offre", 'Établissement', 'Places et prix', 'Statut'],
      ['1', 'Mon offre', 'COLLEGE DE LA TOUR', '25 places', 'confirmée'],
    ]
   await expectIndividualOffersOrBookingsAreFound(page, expectedResults)
 */
export async function expectIndividualOffersOrBookingsAreFound(
  page: Page,
  expectedResults: Array<Array<string>>
): Promise<void> {
  await expectOffersOrBookingsAreFound(
    page,
    expectedResults,
    '(offre|réservation)'
  )
}

/**
 * This function takes a string[][] as a DataTable representing the data
 * in a Table and checks that what is displayed is what is expected.
 * Also checks that the label above is counting the right number of rows: `3 offres`.
 * First row represents the title of columns and is not checked
 *
 * @export
 * @param {Page} page
 * @param {Array<Array<string>>} expectedResults
 * @example
 * const expectedResults = [
      ['', 'Nom de l’offre', 'Dates', 'Prix et participants', 'Établissement', 'Localisation', 'Statut'],
      ['', 'Mon offre', 'Du 01/01/2026 au 01/01/2026', '100€25 participants', 'COLLEGE 123', 'À déterminer', 'publiée'],
    ]
   await expectCollectiveOffersAreFound(page, expectedResults)
 */
export async function expectCollectiveOffersAreFound(
  page: Page,
  expectedResults: string[][]
): Promise<void> {
  await expectOffersOrBookingsAreFound(page, expectedResults, 'offre')
}
