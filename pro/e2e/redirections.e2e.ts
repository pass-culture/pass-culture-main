import { expect, test } from '@playwright/test'
import {
  type APIRequestContext,
  request as playwrightRequest,
} from 'playwright-core'

import { setFeatureFlags } from './helpers/features'
import { BASE_API_URL } from './helpers/sandbox'

test.describe('Redirections', () => {
  let requestContext: APIRequestContext
  test.beforeEach(async () => {
    requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
  })
  test('`/` path redirections', async ({ page }) => {
    await setFeatureFlags(requestContext, [
      {
        name: 'WIP_SWITCH_VENUE',
        isActive: true,
      },
    ])
    await page.goto('/')
    await expect(
      page.getByRole('heading', { name: 'Connectez-vous' })
    ).toBeVisible()
  })
  test('`/inscription` path redirections', async ({ page }) => {
    await setFeatureFlags(requestContext, [
      {
        name: 'WIP_SWITCH_VENUE',
        isActive: true,
      },
    ])
    await page.goto('/inscription')
    await expect(
      page.getByRole('heading', {
        name: 'Commençons par identifier votre profil',
      })
    ).toBeVisible()
  })
})
