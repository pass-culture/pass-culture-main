import { expect, test } from './fixtures/activityData'
import {
  navigateToAdministrationSpace,
  navigateToHubAndPickVenue,
} from './helpers/navigation'

test.describe('Activity Data', () => {
  test('Individual - I should be able to download bookings in CSV and Excel format', async ({
    authenticatedPage: page,
    activityUserData: userData,
  }) => {
    await navigateToHubAndPickVenue(page, userData.venueName)
    await navigateToAdministrationSpace(page)

    await page.getByRole('link', { name: 'Individuel' }).click()
    await expect(page).toHaveURL(/\/individuel$/)

    await page.getByText('Télécharger les réservations').click()

    const csvResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/bookings/csv') &&
        response.request().method() === 'GET'
    )
    await page.getByText('Fichier CSV').click()
    const csvResponse = await csvResponsePromise
    expect(csvResponse.status()).toBe(200)

    await page.getByText('Télécharger les réservations').click()

    const excelResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/bookings/excel') &&
        response.request().method() === 'GET'
    )
    await page.getByText('Microsoft Excel').click()
    const excelResponse = await excelResponsePromise
    expect(excelResponse.status()).toBe(200)
  })
  test('Collective - I should be able to download bookings in CSV and Excel format', async ({
    authenticatedPage: page,
    activityUserData: userData,
  }) => {
    await navigateToHubAndPickVenue(page, userData.venueName)
    await navigateToAdministrationSpace(page)

    await page.getByRole('link', { name: 'Collectif' }).click()
    await expect(page).toHaveURL(/\/collectif$/)

    await page.getByText('Télécharger les offres réservables').click()

    const csvResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/offers/csv') &&
        response.request().method() === 'GET'
    )
    await page.getByText('Fichier CSV').click()
    const csvResponse = await csvResponsePromise
    expect(csvResponse.status()).toBe(200)

    await page.getByText('Télécharger les offres réservables').click()

    const excelResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/offers/excel') &&
        response.request().method() === 'GET'
    )
    await page.getByText('Microsoft Excel').click()
    const excelResponse = await excelResponsePromise
    expect(excelResponse.status()).toBe(200)
  })
})
