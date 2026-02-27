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
  createProUserWithIndividualOffers,
  type IndividualOffersUserData,
} from '../helpers/sandbox'

interface IndividualOffersSession {
  data: IndividualOffersUserData
  storageStatePath: string
}

// Cache for tests that can share a session (read-only tests)
const sharedSessionCache = new Map<string, IndividualOffersSession>()

export const test = base.extend<{
  individualOffersUserData: IndividualOffersUserData
  individualOffersSession: IndividualOffersSession
  authenticatedPage: Page
}>({
  // Shared session for read-only tests (cached across tests)
  individualOffersSession: async ({ browser }, use, testInfo) => {
    const projectName = testInfo.project.name
    const cacheKey = `individual-offers-${projectName}`
    const cached = sharedSessionCache.get(cacheKey)

    if (cached) {
      await use(cached)
      return
    }

    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })

    const userData = await createProUserWithIndividualOffers(requestContext)
    await requestContext.dispose()

    const tempContext = await browser.newContext()
    const tempPage = await tempContext.newPage()
    await login(tempPage, userData.user.email)

    const storageStatePath = path.join(
      testInfo.project.outputDir,
      `auth-state-individual-offers-${projectName}.json`
    )
    await tempContext.storageState({ path: storageStatePath })
    await tempContext.close()

    const session: IndividualOffersSession = {
      data: userData,
      storageStatePath,
    }
    sharedSessionCache.set(cacheKey, session)
    await use(session)
  },

  individualOffersUserData: async ({ individualOffersSession }, use) => {
    await use(individualOffersSession.data)
  },

  authenticatedPage: async (
    { browser, individualOffersSession },
    use,
    testInfo
  ) => {
    const context = await browser.newContext({
      storageState: individualOffersSession.storageStatePath,
      ...testInfo.project.use,
    })
    const page = await context.newPage()

    await use(page)

    await context.close()
  },
})

export { expect }
