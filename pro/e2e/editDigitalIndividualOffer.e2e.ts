import { expect, request as playwrightRequest, test } from '@playwright/test'
import { addDays, format } from 'date-fns'

import { checkAccessibility } from './helpers/accessibility'
import { loginAndNavigate } from './helpers/auth'
import {
  BASE_API_URL,
  createProUserWithBookings,
  createProUserWithVirtualOffer,
} from './helpers/sandbox'

test.describe('Edit digital individual offers', () => {
  test.describe('Display and url modification', () => {
    test('An edited offer should be displayed with 5 navigation links', async ({
      page,
    }) => {
      const requestContext = await playwrightRequest.newContext({
        baseURL: BASE_API_URL,
      })
      const userData = await createProUserWithVirtualOffer(requestContext)
      await requestContext.dispose()

      await loginAndNavigate(
        page,
        userData.user.email,
        '/offre/individuelle/1/recapitulatif/description'
      )

      await expect(page.getByText('Récapitulatif')).toBeVisible()

      await checkAccessibility(page)

      await expect(
        page.getByRole('link', { name: 'Lien actif Description' })
      ).toBeVisible()
      await expect(
        page.getByRole('link', { name: 'Localisation' })
      ).toBeVisible()
      await expect(
        page.getByRole('link', { name: 'Image et vidéo' })
      ).toBeVisible()
      await expect(page.getByRole('link', { name: 'Tarifs' })).toBeVisible()
      await expect(
        page.getByRole('link', { name: 'Informations pratiques' })
      ).toBeVisible()
      await expect(
        page.getByRole('link', { name: 'Réservations' }).nth(1)
      ).toBeVisible()
    })

    test('I should be able to modify the url of a digital offer', async ({
      page,
    }) => {
      const requestContext = await playwrightRequest.newContext({
        baseURL: BASE_API_URL,
      })
      const userData = await createProUserWithVirtualOffer(requestContext)
      await requestContext.dispose()

      await loginAndNavigate(page, userData.user.email, '/offres')

      await expect(page.getByTestId('spinner')).not.toBeVisible()

      // OFFER SUMMARY PAGE
      const firstRow = page.locator('tbody').getByRole('row').first()
      await firstRow.getByRole('button', { name: 'Voir les actions' }).click()
      await page.getByRole('menuitem', { name: 'Voir l’offre' }).click()
      await expect(page).toHaveURL(/\/recapitulatif/)

      // DESCRIPTION EDITION
      await page
        .getByRole('link', { name: 'Modifier la description de l’offre' })
        .click()
      await page.getByText('Enregistrer les modifications').click()

      await expect(
        page.getByRole('heading', { name: 'Description' })
      ).toBeVisible()

      // LOCATION EDITION
      await page.getByText('Localisation').click()
      await expect(page).toHaveURL(/\/localisation/)

      await page
        .getByRole('link', { name: 'Modifier la localisation de l’offre' })
        .click()
      await expect(page).toHaveURL(/\/edition\/localisation/)

      const randomUrl = 'http://myrandomurl.fr/'
      await page.getByLabel(/URL d’accès à l’offre/).fill(randomUrl)
      await page.getByText('Enregistrer les modifications').click()

      await expect(page.getByText('http://myrandomurl.fr/')).toBeVisible()

      // OFFERS LIST
      await page.getByText('Retour à la liste des offres').click()
      await expect(page).toHaveURL(/\/offres/)
      await expect(page.getByTestId('spinner')).not.toBeVisible()
      await expect(
        page.getByRole('heading', { name: 'Offres individuelles' })
      ).toBeVisible()

      const firstRowAgain = page.locator('tbody').getByRole('row').first()
      await firstRowAgain
        .getByRole('button', { name: 'Voir les actions' })
        .click()
      await page.getByRole('menuitem', { name: 'Voir l’offre' }).click()
      await expect(page).toHaveURL(/\/recapitulatif/)

      await page.getByText('Informations pratiques').click()
      await expect(page).toHaveURL(/\/informations_pratiques/)
    })
  })

  test.describe('Modification of an offer with timestamped stocks and bookings', () => {
    test('I should be able to change offer date and it should change date in bookings', async ({
      page,
    }) => {
      const requestContext = await playwrightRequest.newContext({
        baseURL: BASE_API_URL,
      })
      const userData = await createProUserWithBookings(requestContext)
      await requestContext.dispose()

      const newDate = format(addDays(new Date(), 15), 'yyyy-MM-dd')

      await loginAndNavigate(
        page,
        userData.user.email,
        '/offre/individuelle/2/edition/horaires'
      )

      await expect(page.getByText('Modifier l’offre')).toBeVisible()
      await expect(page.getByTestId('spinner')).not.toBeVisible()

      const patchStockPromise = page.waitForResponse(
        (response) =>
          response.url().includes('/stocks/bulk') &&
          response.request().method() === 'PATCH'
      )

      await page
        .getByRole('button', { name: 'Modifier la date' })
        .first()
        .click()

      await page.getByLabel('Date *').first().fill(newDate)
      await page.getByLabel('Date *').nth(1).fill(newDate)

      // Save modifications
      await page.getByText('Valider').click()

      await patchStockPromise

      // Check that booking date has been modified
      await page.goto('/offre/individuelle/2/reservations')
      await expect(page.getByTestId('spinner')).not.toBeVisible()
      await expect(page.locator('[data-label="Nom de l’offre"]')).toContainText(
        format(newDate, 'dd/MM/yyyy')
      )
    })
  })
})
