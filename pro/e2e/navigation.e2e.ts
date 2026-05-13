import { expect, request as playwrightRequest, test } from '@playwright/test'

import { login } from './helpers/auth'
import { BASE_API_URL, createRegularOnboardedProUser } from './helpers/sandbox'

test.describe('Navigation', () => {
  let userEmail: string

  test.beforeEach(async () => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })

    const userData = await createRegularOnboardedProUser(requestContext)
    userEmail = userData.user.email

    await requestContext.dispose()
  })

  test('I should see the top of the page when changing page', async ({
    page,
  }) => {
    await login(page, userEmail)

    const collectivePageLink = page.getByRole('link', {
      name: 'Gérer la page pour les enseignants',
    })
    await expect(collectivePageLink).toBeVisible()
    await collectivePageLink.scrollIntoViewIfNeeded()

    const contentWrapper = page.locator('#content-wrapper')
    const scrollTopBefore = await contentWrapper.evaluate((el) => el.scrollTop)
    expect(scrollTopBefore).toBeGreaterThan(0)

    await collectivePageLink.click()

    await expect(page).toHaveURL(/\/partenaire\/page-collective/)

    const backToNavLink = page.locator('#top-page')
    await expect(backToNavLink).toBeFocused({ timeout: 1000 })

    const scrollTopAfter = await contentWrapper.evaluate((el) => el.scrollTop)
    expect(scrollTopAfter).toBe(0)
  })
})
