import { type APIRequestContext, expect, request, test } from '@playwright/test'
import { addDays, format } from 'date-fns'

import { loginAndNavigate } from './helpers/auth'
import { isPatchStocksResponse } from './helpers/requests'
import {
  BASE_API_URL,
  createProUserWithBookings,
  createProUserWithDeletableEventStockWithBookings,
  createProUserWithVirtualOffer,
} from './helpers/sandbox'

test.describe('Individual Offer Creation and Edition', () => {
  let requestContext: APIRequestContext
  let userData: { user: { email: string } }

  test.beforeEach(async () => {
    requestContext = await request.newContext({
      baseURL: BASE_API_URL,
    })
    userData = await createProUserWithVirtualOffer(requestContext)

    await requestContext.dispose()
  })

  test('I can navigate from creation to edition', async ({ page }) => {
    await loginAndNavigate(
      page,
      userData.user.email,
      '/offre/individuelle/creation/description'
    )

    const titleInput = page.getByLabel(/Titre de l’offre/)
    await expect(titleInput).toHaveValue('')

    await page.goto('/offre/individuelle/1/edition/description')
    await expect(page.getByTestId('spinner')).not.toBeVisible()

    await expect(titleInput).toHaveValue('Mon offre virtuelle')
  })

  test('I can navigate from edition to creation', async ({ page }) => {
    await loginAndNavigate(
      page,
      userData.user.email,
      '/offre/individuelle/1/edition/description'
    )

    const titleInput = page.getByLabel(/Titre de l’offre/)
    await expect(titleInput).toHaveValue('Mon offre virtuelle')

    await page.goto('/offre/individuelle/creation/description')
    await expect(page.getByTestId('spinner')).not.toBeVisible()

    await expect(titleInput).toHaveValue('')
  })

  test('I should see a warning modal when editing a stock with bookings and update only after confirmation', async ({
    page,
  }) => {
    const bookingRequestContext = await request.newContext({
      baseURL: BASE_API_URL,
    })
    const bookingUserData = await createProUserWithBookings(
      bookingRequestContext
    )
    await bookingRequestContext.dispose()

    expect(bookingUserData.eventOfferId).toBeDefined()

    await loginAndNavigate(
      page,
      bookingUserData.user.email,
      `/offre/individuelle/${bookingUserData.eventOfferId}/edition/horaires`
    )

    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await page.getByRole('button', { name: 'Modifier la date' }).first().click()

    const newDate = format(addDays(new Date(), 15), 'yyyy-MM-dd')
    await page.getByLabel('Date *').first().fill(newDate)
    await page.getByLabel('Date *').nth(1).fill(newDate)

    await page.getByRole('button', { name: 'Valider' }).click()

    await expect(
      page.getByRole('heading', {
        name: 'Modifier la date des réservations existantes ?',
      })
    ).toBeVisible()

    await expect(
      page.getByRole('button', { name: 'Fermer la boite de dialogue' })
    ).toBeFocused()

    await Promise.all([
      page.waitForResponse(isPatchStocksResponse),
      page.getByRole('button', { name: 'Confirmer la modification' }).click(),
    ])
  })

  test('I should see a warning modal when deleting a stock with bookings and delete only after confirmation', async ({
    page,
  }) => {
    const bookingRequestContext = await request.newContext({
      baseURL: BASE_API_URL,
    })
    const bookingUserData =
      await createProUserWithDeletableEventStockWithBookings(
        bookingRequestContext
      )
    await bookingRequestContext.dispose()

    await loginAndNavigate(
      page,
      bookingUserData.user.email,
      `/offre/individuelle/${bookingUserData.eventOfferId}/edition/horaires`
    )

    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await page
      .getByRole('button', { name: 'Supprimer la date' })
      .first()
      .click()

    await expect(
      page.getByRole('button', { name: 'Confirmer la suppression' })
    ).toBeVisible()

    const deleteStockPromise = page.waitForResponse(
      (response) =>
        response.url().includes('/stocks/delete') &&
        response.request().method() === 'POST' &&
        response.status() === 200
    )

    await page.getByRole('button', { name: 'Confirmer la suppression' }).click()
    await deleteStockPromise
  })

  test('I should delete directly without warning modal when stock has no bookings', async ({
    page,
  }) => {
    const virtualOfferRequestContext = await request.newContext({
      baseURL: BASE_API_URL,
    })
    const virtualOfferUserData = await createProUserWithVirtualOffer(
      virtualOfferRequestContext
    )
    await virtualOfferRequestContext.dispose()

    await loginAndNavigate(
      page,
      virtualOfferUserData.user.email,
      '/offre/individuelle/1/edition/horaires'
    )

    await expect(page.getByTestId('spinner')).toHaveCount(0)

    const deleteStockPromise = page.waitForResponse(
      (response) =>
        response.url().includes('/stocks/delete') &&
        response.request().method() === 'POST' &&
        response.status() === 200
    )

    await page
      .getByRole('button', { name: 'Supprimer la date' })
      .first()
      .click()

    await deleteStockPromise

    await expect(
      page.getByRole('button', { name: 'Confirmer la suppression' })
    ).not.toBeVisible()
  })
})
