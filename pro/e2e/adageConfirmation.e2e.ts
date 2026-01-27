import { expect, request as playwrightRequest, test } from '@playwright/test'

import { expectCollectiveOffersAreFound } from './helpers/assertions'
import { login } from './helpers/auth'
import {
  BASE_API_URL,
  createProUserWithActiveCollectiveOffer,
  sandboxCall,
} from './helpers/sandbox'

const BOOKABLE_OFFERS_COLUMNS = [
  '',
  'Nom de l’offre',
  'Dates',
  'Prix et participants',
  'Établissement',
  'Localisation',
  'Statut',
]

function collectiveFormatEventDate(date: string): string {
  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    timeZone: 'Europe/Paris',
  }).format(new Date(date))
}

const EMAIL1 = 'collectiveofferfactory+booking@example.com'
const EMAIL2 = 'collectiveofferfactory+booking@example2.com'

test.describe('Adage confirmation', () => {
  test('I should be able to search offers with status filters after adage confirmation or cancellation and see expected results', async ({
    page,
  }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })

    const userData =
      await createProUserWithActiveCollectiveOffer(requestContext)

    const userLogin = userData.user.email
    const offer = userData.offer
    const stock = userData.stock
    const providerApiKey = userData.providerApiKey

    const clearEmailResponse = await requestContext.get(
      `${BASE_API_URL}/sandboxes/clear_email_list`
    )
    expect(clearEmailResponse.status()).toBe(200)

    await login(page, userLogin)
    await page.goto('/offres/collectives')

    await page.waitForResponse(
      (response) =>
        response.url().includes(`/collective/bookable-offers`) &&
        response.status() === 200
    )

    await page
      .getByRole('link', { name: `N°${offer.id} ${offer.name}` })
      .click()

    await page.waitForResponse(
      (response) =>
        response.url().includes(`/collective/offers/${offer.id}`) &&
        response.status() === 200
    )

    await expect(page.getByTestId('page-title-announcer')).toContainText(
      'Récapitulatif'
    )
    await expect(page.getByText('publiée').first()).toBeVisible()

    await page.goto('/offres/collectives')

    const bookResponse = await requestContext.post(
      `${BASE_API_URL}/v2/collective/adage_mock/offer/${offer.id}/book`,
      {
        headers: {
          Authorization: `Bearer ${providerApiKey}`,
          'Content-Type': 'application/json',
        },
        data: {},
      }
    )
    expect(bookResponse.status()).toBe(200)
    const bookingData = await bookResponse.json()
    const bookingId = bookingData.bookingId

    const emailResponse1 = await sandboxCall<{
      To: string
      params: { BOOKING_ID: number }
    }>(requestContext, 'GET', `${BASE_API_URL}/sandboxes/get_unique_email`)
    expect(emailResponse1.To).toBe(`${EMAIL1}, ${EMAIL2}`)
    expect(emailResponse1.params.BOOKING_ID).toBe(bookingId)

    await page.getByText('Filtrer').click()

    await page.getByRole('button', { name: 'Statut' }).click()
    await page.getByTestId('panel-scrollable').getByText('Préréservée').click()

    await page.getByRole('button', { name: 'Statut' }).click()

    await page.getByText('Rechercher').click({ force: true })

    await page.waitForResponse(
      (response) =>
        response.url().includes('/collective/bookable-offers') &&
        response.url().includes('status=PREBOOKED') &&
        response.status() === 200
    )

    let expectedResults = [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        `N°${offer.id}${offer.name}`,
        collectiveFormatEventDate(stock.startDatetime),
        `100€25 participants`,
        'DE LA TOUR',
        'À déterminer',
        'préréservée',
      ],
    ]

    await expectCollectiveOffersAreFound(page, expectedResults)

    await expect(
      page.getByText('En attente de réservation par le chef d’établissement')
    ).toBeVisible()

    const clearEmailResponse2 = await requestContext.get(
      `${BASE_API_URL}/sandboxes/clear_email_list`
    )
    expect(clearEmailResponse2.status()).toBe(200)

    const confirmResponse = await requestContext.post(
      `${BASE_API_URL}/v2/collective/adage_mock/bookings/${bookingId}/confirm`,
      {
        headers: {
          Authorization: `Bearer ${providerApiKey}`,
          'Content-Type': 'application/json',
        },
        data: {},
      }
    )
    expect(confirmResponse.status()).toBe(204)

    const emailResponse2 = await sandboxCall<{
      To: string
      Bcc: string
      params: { BOOKING_ID: number }
    }>(requestContext, 'GET', `${BASE_API_URL}/sandboxes/get_unique_email`)
    expect(emailResponse2.To).toBe(EMAIL1)
    expect(emailResponse2.Bcc).toBe(EMAIL2)
    expect(emailResponse2.params.BOOKING_ID).toBe(bookingId)

    await page.getByText('Réinitialiser les filtres').click()

    await expect(page.getByRole('button', { name: 'Statut' })).toBeVisible()

    await page.getByRole('button', { name: 'Statut' }).click()
    await page
      .getByTestId('panel-scrollable')
      .getByText('Réservée', { exact: true })
      .click()

    await page.getByRole('button', { name: 'Statut' }).click()

    await page.getByText('Rechercher').click({ force: true })

    await page.waitForResponse(
      (response) =>
        response.url().includes('/collective/bookable-offers') &&
        response.url().includes('status=BOOKED') &&
        response.status() === 200
    )

    expectedResults = [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        `N°${offer.id}${offer.name}`,
        collectiveFormatEventDate(stock.startDatetime),
        `100€25 participants`,
        'DE LA TOUR',
        'À déterminer',
        'réservée',
      ],
    ]

    await expectCollectiveOffersAreFound(page, expectedResults)

    await page.getByText('Réinitialiser les filtres').click()

    await expect(page.getByRole('button', { name: 'Statut' })).toBeVisible()

    const clearEmailResponse3 = await requestContext.get(
      `${BASE_API_URL}/sandboxes/clear_email_list`
    )
    expect(clearEmailResponse3.status()).toBe(200)

    await page.getByRole('button', { name: 'Voir les actions' }).click()
    await page.getByText('Annuler la réservation').click()
    await page.getByTestId('confirm-dialog-button-confirm').click()

    await page.waitForResponse(
      (response) =>
        response.url().includes('/collective/bookable-offers') &&
        response.status() === 200
    )

    await expect(
      page.locator('[data-testid="global-snack-bar-success-0"]').filter({
        hasText:
          'Vous avez annulé la réservation de cette offre. Elle n’est donc plus visible sur ADAGE.',
      })
    ).toBeVisible()

    const emailResponse3 = await sandboxCall<{
      To: string
      Bcc: string
    }>(requestContext, 'GET', `${BASE_API_URL}/sandboxes/get_unique_email`)
    expect(emailResponse3.To).toBe(EMAIL1)
    expect(emailResponse3.Bcc).toBe(EMAIL2)

    await expect(page.getByText('annulée')).toBeVisible()

    expectedResults = [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        `N°${offer.id}${offer.name}`,
        collectiveFormatEventDate(stock.startDatetime),
        `100€25 participants`,
        'DE LA TOUR',
        'À déterminer',
        'annulée',
      ],
    ]

    await expectCollectiveOffersAreFound(page, expectedResults)

    await requestContext.dispose()
  })
})
