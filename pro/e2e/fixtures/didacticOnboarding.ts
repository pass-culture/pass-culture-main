// biome-ignore assist/source/organizeImports: Unfixable.
import {
  expect,
  type APIRequestContext,
  request as playwrightRequest,
} from '@playwright/test'

import { test as base } from './common'
import { BASE_API_URL, createRegularProUser } from '../helpers/sandbox'
import { setFeatureFlags } from '../helpers/features'

export const test = base.extend<{
  callSandbox: (ctx: APIRequestContext) => Promise<any>
  offerDraft: { id: number; name: string; venueName: string }
}>({
  // biome-ignore lint/correctness/noUnusedFunctionParameters: Needed by Playwright
  callSandbox: async ({ browser }, use) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const callSandbox = (ctx: APIRequestContext): Promise<any> => {
      return createRegularProUser(ctx)
    }
    await setFeatureFlags(requestContext, [
      { name: 'WIP_SWITCH_VENUE', isActive: false },
    ])

    await use(callSandbox)
  },
})

export { expect }
