import * as path from 'node:path'
import {
  test as base,
  expect,
  type Page,
  request as playwrightRequest,
} from '@playwright/test'

import { doLogin } from '../helpers/auth'
import {
  BASE_API_URL,
  createRegularOnboardedProUserWithNonAttachedOfferer,
  type ProUserDataWithNonAttachedOfferer,
} from '../helpers/sandbox'
import { joinExistingVenueSpace } from '../helpers/switchVenue'

interface NonAttachedSession {
  data: ProUserDataWithNonAttachedOfferer
  storageStatePath: string
}

// Cache for tests that can share a session (read-only tests)
const sharedSessionCache = new Map<string, NonAttachedSession>()

export const test = base.extend<{
  nonAttachedSession: NonAttachedSession
  authenticatedPage: Page
}>({
  // Shared session for read-only tests (cached across tests)
  nonAttachedSession: async ({ browser }, use, testInfo) => {
    const projectName = testInfo.project.name
    const cacheKey = `non-attached-${projectName}`
    const cached = sharedSessionCache.get(cacheKey)

    if (cached) {
      await use(cached)
      return
    }

    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })

    const userData =
      await createRegularOnboardedProUserWithNonAttachedOfferer(requestContext)
    await requestContext.dispose()

    const tempContext = await browser.newContext()
    const tempPage = await tempContext.newPage()
    await doLogin(tempPage, userData.user.email)

    await joinExistingVenueSpace(tempPage, userData.nonAttachedSiret)

    const storageStatePath = path.join(
      testInfo.project.outputDir,
      `auth-state-non-attached-${projectName}.json`
    )
    await tempContext.storageState({ path: storageStatePath })
    await tempContext.close()

    const session: NonAttachedSession = {
      data: userData,
      storageStatePath,
    }
    sharedSessionCache.set(cacheKey, session)
    await use(session)
  },

  authenticatedPage: async ({ browser, nonAttachedSession }, use, testInfo) => {
    const context = await browser.newContext({
      storageState: nonAttachedSession.storageStatePath,
      ...testInfo.project.use,
    })
    const page = await context.newPage()

    await use(page)

    await context.close()
  },
})

export { expect }
