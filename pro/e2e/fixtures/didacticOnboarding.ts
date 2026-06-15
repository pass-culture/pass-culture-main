import { type APIRequestContext, expect } from '@playwright/test'

import { createRegularProUser } from '../helpers/sandbox'
import { test as base } from './common'

export const test = base.extend<{
  callSandbox: (ctx: APIRequestContext) => Promise<any>
  offerDraft: { id: number; name: string; venueName: string }
}>({
  // biome-ignore lint/correctness/noUnusedFunctionParameters: Needed by Playwright
  callSandbox: async ({ browser }, use) => {
    const callSandbox = (ctx: APIRequestContext): Promise<any> => {
      return createRegularProUser(ctx)
    }

    await use(callSandbox)
  },
})

export { expect }
