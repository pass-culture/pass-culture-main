import { type APIRequestContext, expect } from '@playwright/test'

import { createRegularOnboardedProUser } from '../helpers/sandbox'
import { test as base } from './common'

export const test = base.extend<{
  callSandbox: (ctx: APIRequestContext) => Promise<any>
}>({
  // biome-ignore lint/correctness/noUnusedFunctionParameters: Needed by Playwright
  callSandbox: async ({ browser }, use) => {
    const callSandbox = (ctx: APIRequestContext): Promise<any> => {
      return createRegularOnboardedProUser(ctx)
    }

    await use(callSandbox)
  },
})

export { expect }
