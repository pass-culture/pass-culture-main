// biome-ignore assist/source/organizeImports: Unfixable.
import { expect, type APIRequestContext } from '@playwright/test'

import { test as base } from './common'
import { createRegularOnboardedProUser } from '../helpers/sandbox'

export const test = base.extend<{
  callSandbox: (ctx: APIRequestContext) => Promise<any>
}>({
  callSandbox: async ({ browser }, use) => {
    const callSandbox = (ctx: APIRequestContext): Promise<any> => {
      return createRegularOnboardedProUser(ctx)
    }

    await use(callSandbox)
  },
})

export { expect }
