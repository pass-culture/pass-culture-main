import { type APIRequestContext, expect, type Page } from '@playwright/test'
import { request as playwrightRequest } from 'playwright-core'

import { mockAddressSearch } from '../helpers/address'
import { setFeatureFlags } from '../helpers/features'
import { navigateToHubAndPickVenue } from '../helpers/navigation'
import {
  BASE_API_URL,
  createProUserWithCollectiveOffers,
} from '../helpers/sandbox'
import { test as base } from './common'

export const test = base.extend<{
  callSandbox: (ctx: APIRequestContext) => Promise<any>
  offerDraft: { id: number; name: string; venueName: string }
  authenticatedPage: Page
}>({
  authenticatedPage: async ({ browser, authSession }, use, testInfo) => {
    const context = await browser.newContext({
      storageState: authSession.storageStatePath,
      ...testInfo.project.use,
    })
    const page = await context.newPage()

    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    await setFeatureFlags(requestContext, [
      {
        name: 'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS',
        isActive: true,
      },
    ])
    const venueName = 'Mon Lieu A'
    await navigateToHubAndPickVenue(page, venueName)
    await page.goto('/offre/creation')
    await mockAddressSearch(page)

    await use(page)

    await context.close()
  },
  // biome-ignore lint/correctness/noUnusedFunctionParameters: Needed by Playwright
  callSandbox: async ({ browser }, use) => {
    const callSandbox = (ctx: APIRequestContext): Promise<any> => {
      return createProUserWithCollectiveOffers(ctx)
    }

    await use(callSandbox)
  },
  offerDraft: async ({ authSession }, use) => {
    await use(authSession.data.offerDraft)
  },
})

export { expect }
