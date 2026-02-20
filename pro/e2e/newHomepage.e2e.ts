import test, { expect, request as playwrightRequest } from '@playwright/test'

import { login } from './helpers/auth'
import { setFeatureFlags } from './helpers/features'
import { BASE_API_URL, createProUserWithVirtualOffer } from './helpers/sandbox'

test.describe('New Homepage', () => {
  test('I should see the individual homepage', async ({ page }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const userData = await createProUserWithVirtualOffer(requestContext)
    await setFeatureFlags(requestContext, [
      { name: 'WIP_SWITCH_VENUE', isActive: true },
      { name: 'WIP_ENABLE_NEW_PRO_HOME', isActive: true },
    ])
    await requestContext.dispose()

    await login(page, userData.user.email)
    await page.goto('/accueil')

    await expect(
      page.getByRole('heading', {
        level: 1,
        name: /Votre espace/,
      })
    ).toBeVisible()
  })
})
