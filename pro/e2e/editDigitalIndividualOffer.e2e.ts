import { expect, request as playwrightRequest, test } from '@playwright/test'
import { addDays, format } from 'date-fns'

import { checkAccessibility } from './helpers/accessibility'
import { loginAndNavigate } from './helpers/auth'
import { isPatchStocksResponse } from './helpers/requests'
import {
  BASE_API_URL,
  createProUserWithBookings,
  createProUserWithVirtualOffer,
} from './helpers/sandbox'

test.describe('Edit digital individual offers', () => {
  test.describe('Display and url modification', () => {
    test('An edited offer should be displayed with 6 navigation links', async ({
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
        '/offre/individuelle/1/visibilite'
      )
      await expect(
        page.getByRole('heading', {
          level: 2,
          name: 'Actions de mise en avant',
        })
      ).toBeVisible()
      await expect(page.getByTestId('spinner')).toHaveCount(0)

      await checkAccessibility(page)

      await expect(
        page.getByRole('link', { name: 'Lien actif Visibilité' })
      ).toBeVisible()
      await expect(
        page.getByRole('link', { name: 'Description' })
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
      await page.getByRole('button', { name: 'Individuel' }).click() // Open section
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

      // OFFER EXPOSURE PAGE
      const firstRow = page.locator('tbody').getByRole('row').first()
      await firstRow.getByRole('button', { name: 'Voir les actions' }).click()
      await page.getByRole('menuitem', { name: 'Voir l’offre' }).click()
      await expect(page).toHaveURL(/\/visibilite/)

      // DESCRIPTION EDITION
      await page.getByRole('link', { name: 'Description' }).click()
      await expect(page).toHaveURL(/\/edition\/description/)
      await page.getByLabel(/Description/).fill('Une description modifiée')
      await page.getByText('Enregistrer les modifications').click()
      await expect(
        page.getByText('Votre offre a bien été modifiée.')
      ).toBeVisible()

      // LOCATION EDITION
      await page.getByRole('link', { name: 'Localisation' }).click()
      await expect(page).toHaveURL(/\/edition\/localisation/)

      const randomUrl = 'http://myrandomurl.fr/'
      await page.getByLabel(/URL d’accès à l’offre/).fill(randomUrl)
      await page.getByText('Enregistrer les modifications').click()
      await expect(
        page.getByText('Votre offre a bien été modifiée.')
      ).toBeVisible()
      await expect(page.getByLabel(/URL d’accès à l’offre/)).toHaveValue(
        randomUrl
      )
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
      await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
      await expect(page.getByTestId('spinner')).toHaveCount(0)

      await page
        .getByRole('button', { name: 'Modifier la date' })
        .first()
        .click()

      await page.getByLabel('Date *').first().fill(newDate)
      await page.getByLabel('Date *').nth(1).fill(newDate)

      // Save modifications
      await page.getByRole('button', { name: 'Valider' }).click()

      await expect(
        page.getByRole('heading', {
          name: 'Modifier la date des réservations existantes ?',
        })
      ).toBeVisible()

      await Promise.all([
        page.waitForResponse(isPatchStocksResponse),
        page.getByRole('button', { name: 'Confirmer la modification' }).click(),
      ])

      // Check that booking date has been modified
      await page.goto('/offre/individuelle/2/reservations')
      await expect(page.getByTestId('spinner')).not.toBeVisible()
      await expect(page.locator('[data-label="Nom de l’offre"]')).toContainText(
        format(newDate, 'dd/MM/yyyy')
      )
    })
  })
})
