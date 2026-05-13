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
  createRegularOnboardedProUser,
  type ProUserAlreadyOnboarded,
} from '../helpers/sandbox'

interface ActivityDataSession {
  data: ProUserAlreadyOnboarded
  storageStatePath: string
}

// Cache for tests that can share a session (read-only tests)
const sharedSessionCache = new Map<string, ActivityDataSession>()

export const test = base.extend<{
  activityUserData: ProUserAlreadyOnboarded
  activityDataSession: ActivityDataSession
  authenticatedPage: Page
}>({
  // Shared session for read-only tests (cached across tests)
  activityDataSession: async ({ browser }, use, testInfo) => {
    const projectName = testInfo.project.name
    const cacheKey = `activity-data-${projectName}`
    const cached = sharedSessionCache.get(cacheKey)

    if (cached) {
      await use(cached)
      return
    }

    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })

    const userData = await createRegularOnboardedProUser(requestContext)
    await requestContext.dispose()

    const tempContext = await browser.newContext()
    const tempPage = await tempContext.newPage()
    await login(tempPage, userData.user.email)

    const storageStatePath = path.join(
      testInfo.project.outputDir,
      `auth-state-activity-data-${projectName}.json`
    )
    await tempContext.storageState({ path: storageStatePath })
    await tempContext.close()

    const session: ActivityDataSession = {
      data: userData,
      storageStatePath,
    }
    sharedSessionCache.set(cacheKey, session)
    await use(session)
  },

  activityUserData: async ({ activityDataSession }, use) => {
    await use(activityDataSession.data)
  },

  authenticatedPage: async (
    { browser, activityDataSession },
    use,
    testInfo
  ) => {
    const context = await browser.newContext({
      storageState: activityDataSession.storageStatePath,
      ...testInfo.project.use,
    })
    const page = await context.newPage()

    await use(page)

    await context.close()
  },
})

export { expect }
