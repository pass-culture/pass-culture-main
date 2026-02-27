import * as path from 'node:path'
import {
  test as base,
  expect,
  type Page,
  request as playwrightRequest,
} from '@playwright/test'

import { login } from '../helpers/auth'
import {
  BASE_API_URL,
  type CollectiveOffersUserData,
  createProUserWithCollectiveOffers,
} from '../helpers/sandbox'

interface CollectiveOffersSession {
  data: CollectiveOffersUserData
  storageStatePath: string
}

const sharedSessionCache = new Map<string, CollectiveOffersSession>()

export const test = base.extend<{
  collectiveOffersUserData: CollectiveOffersUserData
  collectiveOffersSession: CollectiveOffersSession
  authenticatedPage: Page
}>({
  collectiveOffersSession: async ({ browser }, use, testInfo) => {
    const projectName = testInfo.project.name
    const cacheKey = `collective-offers-${projectName}`
    const cached = sharedSessionCache.get(cacheKey)

    if (cached) {
      await use(cached)
      return
    }

    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })

    const userData = await createProUserWithCollectiveOffers(requestContext)
    await requestContext.dispose()

    const tempContext = await browser.newContext()
    const tempPage = await tempContext.newPage()
    await login(tempPage, userData.user.email)

    const storageStatePath = path.join(
      testInfo.project.outputDir,
      `auth-state-collective-offers-${projectName}.json`
    )
    await tempContext.storageState({ path: storageStatePath })
    await tempContext.close()

    const session: CollectiveOffersSession = {
      data: userData,
      storageStatePath,
    }
    sharedSessionCache.set(cacheKey, session)
    await use(session)
  },

  collectiveOffersUserData: async ({ collectiveOffersSession }, use) => {
    await use(collectiveOffersSession.data)
  },

  authenticatedPage: async (
    { browser, collectiveOffersSession },
    use,
    testInfo
  ) => {
    const context = await browser.newContext({
      storageState: collectiveOffersSession.storageStatePath,
      ...testInfo.project.use,
    })
    const page = await context.newPage()

    await use(page)

    await context.close()
  },
})

export { expect }
