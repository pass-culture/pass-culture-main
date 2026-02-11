// biome-ignore assist/source/organizeImports: Unfixable.
import { expect, type APIRequestContext } from '@playwright/test'

import { test as base } from './common'
import { createProUserWithCollectiveOffer } from '../helpers/sandbox'

export const test = base.extend<{
  callSandbox: (ctx: APIRequestContext) => Promise<any>
  offerDraft: { id: number; name: string; venueName: string }
}>({
  callSandbox: async ({ browser }, use) => {
    const callSandbox = (ctx: APIRequestContext): Promise<any> => {
      return createProUserWithCollectiveOffer(ctx)
    }

    await use(callSandbox)
  },
  offerDraft: async ({ authSession }, use) => {
    await use(authSession.data.offerDraft)
  },
})

export { expect }
