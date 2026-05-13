import { expect, request as playwrightRequest, test } from '@playwright/test'

import { doLogin } from './helpers/auth'
import { setFeatureFlags } from './helpers/features'
import {
  BASE_API_URL,
  createProUserWithFinancialDataAnd3Venues,
} from './helpers/sandbox'
import { navigateToHubAndPickVenue } from './helpers/switchVenue'

test.describe('Hub', () => {
  test('I should be able to switch from one venue to another', async ({
    page,
  }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })

    const userData =
      await createProUserWithFinancialDataAnd3Venues(requestContext)
    await setFeatureFlags(requestContext, [
      { name: 'WIP_ENABLE_NEW_PRO_HOME', isActive: true },
    ])
    await requestContext.dispose()

    await doLogin(page, userData.user.email)
    await navigateToHubAndPickVenue(page, 'Mon lieu 2')
    await expect
      .soft(
        page.getByRole('heading', {
          level: 1,
          name: 'Votre espace Mon lieu 2',
        })
      )
      .toBeVisible()
    await navigateToHubAndPickVenue(page, 'Mon lieu 3')

    await expect
      .soft(
        page.getByRole('heading', {
          level: 1,
          name: 'Votre espace Mon lieu 3',
        })
      )
      .toBeVisible()
  })
})
