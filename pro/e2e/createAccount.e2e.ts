import { randomUUID } from 'node:crypto'
import { expect, request as playwrightRequest, test } from '@playwright/test'

import { checkAccessibility } from './helpers/accessibility'
import { BASE_API_URL, sandboxCall } from './helpers/sandbox'

interface EmailResponse {
  To: string
  params: {
    EMAIL_VALIDATION_LINK: string
  }
}

test.describe('Account creation', () => {
  test.beforeEach(async () => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })

    const clearResponse = await requestContext.fetch(
      `${BASE_API_URL}/sandboxes/clear_email_list`,
      { method: 'GET' }
    )
    expect(clearResponse.status()).toBe(200)

    await requestContext.dispose()
  })

  test('I should be able to create an account', async ({ page }) => {
    const randomEmail = `jean${randomUUID()}@example.com`

    await page.goto('/inscription/compte/creation')

    await page.getByLabel(/Nom/).fill('LEMOINE')
    await page.getByLabel(/Prénom/).fill('Jean')
    await page.getByLabel(/Adresse email/).fill(randomEmail)
    await page.getByLabel(/Mot de passe/).fill('user@AZERTY123')

    await checkAccessibility(page)

    const signupResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/users/signup') &&
        response.request().method() === 'POST'
    )
    await page.getByRole('button', { name: 'S’inscrire' }).click()
    const signupResponse = await signupResponsePromise
    expect(signupResponse.status()).toBe(204)

    await expect(page).toHaveURL(/\/inscription\/compte\/confirmation/)
    await expect(
      page.getByRole('heading', { name: 'Validez votre adresse email' })
    ).toBeVisible()

    await checkAccessibility(page)

    const emailRequestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })

    const emailData = await sandboxCall<EmailResponse>(
      emailRequestContext,
      'GET',
      `${BASE_API_URL}/sandboxes/get_unique_email`
    )

    expect(emailData.To).toBe(randomEmail)

    await emailRequestContext.dispose()

    await page.goto(emailData.params.EMAIL_VALIDATION_LINK)

    await expect(page).toHaveURL(/\/inscription\/structure\/recherche/)
    await expect(
      page.getByRole('link', { name: /Aller au contenu/ })
    ).toBeFocused()

    await checkAccessibility(page)
  })
})
