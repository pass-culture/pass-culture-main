import { expect, request as playwrightRequest, test } from '@playwright/test'

import { loginAndNavigate } from './helpers/auth'
import { BASE_API_URL, sandboxCall } from './helpers/sandbox'

interface ProUserResponse {
  user: {
    email: string
  }
}

test.describe('Navigation', () => {
  let userEmail: string

  test.beforeEach(async () => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })

    const userData = await sandboxCall<ProUserResponse>(
      requestContext,
      'GET',
      `${BASE_API_URL}/sandboxes/pro/create_regular_pro_user_already_onboarded`
    )
    userEmail = userData.user.email

    await requestContext.dispose()
  })

  test('I should see the top of the page when changing page', async ({
    page,
  }) => {
    await loginAndNavigate(page, userEmail, '/accueil')

    const nextStepsHeading = page.getByRole('heading', {
      name: /Prochaines étapes/,
    })
    await expect(nextStepsHeading).toBeVisible()
    await nextStepsHeading.scrollIntoViewIfNeeded()

    const contentWrapper = page.locator('#content-wrapper')
    const scrollTopBefore = await contentWrapper.evaluate((el) => el.scrollTop)
    expect(scrollTopBefore).toBeGreaterThan(0)

    await page
      .getByRole('link', { name: 'Gérer la page pour les enseignants' })
      .click()

    await expect(page).toHaveURL(/\/structures\/\d+\/lieux\/\d+\/collectif/)

    const backToNavLink = page.locator('#back-to-nav-link')
    await expect(backToNavLink).toBeFocused({ timeout: 1000 })

    const scrollTopAfter = await contentWrapper.evaluate((el) => el.scrollTop)
    expect(scrollTopAfter).toBe(0)
  })
})
