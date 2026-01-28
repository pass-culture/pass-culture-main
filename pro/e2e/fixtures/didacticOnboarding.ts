import * as path from 'node:path'
import {
  test as base,
  expect,
  type Page,
  request as playwrightRequest,
} from '@playwright/test'

import { login } from '../helpers/auth'
import { BASE_API_URL, type ProUserData, sandboxCall } from '../helpers/sandbox'

interface DidacticOnboardingSession {
  data: ProUserData
  storageStatePath: string
}

const sharedSessionCache = new Map<string, DidacticOnboardingSession>()

async function createDidacticUser(
  requestContext: ReturnType<
    typeof playwrightRequest.newContext
  > extends Promise<infer T>
    ? T
    : never
): Promise<ProUserData> {
  return await sandboxCall<ProUserData>(
    requestContext,
    'GET',
    `${BASE_API_URL}/sandboxes/pro/create_regular_pro_user`
  )
}

export const test = base.extend<{
  didacticUserData: ProUserData
  didacticSession: DidacticOnboardingSession
  authenticatedPage: Page
  page: Page
}>({
  didacticSession: async ({ browser }, use, testInfo) => {
    const projectName = testInfo.project.name
    const cacheKey = `didactic-${projectName}`
    const cached = sharedSessionCache.get(cacheKey)

    if (cached) {
      await use(cached)
      return
    }

    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })

    const userData = await createDidacticUser(requestContext)
    await requestContext.dispose()

    const tempContext = await browser.newContext()
    const tempPage = await tempContext.newPage()
    await login(tempPage, userData.user.email)

    const storageStatePath = path.join(
      testInfo.project.outputDir,
      `auth-state-didactic-${projectName}.json`
    )
    await tempContext.storageState({ path: storageStatePath })
    await tempContext.close()

    const session: DidacticOnboardingSession = {
      data: userData,
      storageStatePath,
    }
    sharedSessionCache.set(cacheKey, session)
    await use(session)
  },

  didacticUserData: async ({ didacticSession }, use) => {
    await use(didacticSession.data)
  },

  authenticatedPage: async ({ browser, didacticSession }, use, testInfo) => {
    const context = await browser.newContext({
      storageState: didacticSession.storageStatePath,
      ...testInfo.project.use,
    })
    const page = await context.newPage()

    await use(page)

    await context.close()
  },

  page: async ({ browser }, use, testInfo) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })

    const userData = await createDidacticUser(requestContext)
    await requestContext.dispose()

    const context = await browser.newContext({
      ...testInfo.project.use,
    })
    const page = await context.newPage()
    await login(page, userData.user.email)

    await use(page)

    await context.close()
  },
})

export { expect }
