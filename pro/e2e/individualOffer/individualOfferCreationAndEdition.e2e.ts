import { type APIRequestContext, expect, request, test } from '@playwright/test'

import { loginAndNavigate } from '../helpers/auth'
import { BASE_API_URL, createProUserWithVirtualOffer } from '../helpers/sandbox'

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
})
