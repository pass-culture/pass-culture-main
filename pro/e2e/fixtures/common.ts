import * as path from 'node:path'
import {
  type APIRequestContext,
  test as base,
  expect,
  type Page,
  request as playwrightRequest,
} from '@playwright/test'

import { checkAccessibility as checkAccessibilityHelper } from '../helpers/accessibility'
import { doLogin } from '../helpers/auth'

interface AuthSession {
  data: any
  storageStatePath: string
}

const sessionCache = new Map<string, AuthSession>()

export const test = base.extend<{
  callSandbox: (ctx: APIRequestContext) => Promise<any>
  checkAccessibility: (disabledRules?: string[]) => Promise<void>
  authSession: AuthSession
  authenticatedPage: Page
}>({
  authSession: async ({ browser, callSandbox }, use, testInfo) => {
    const projectName = `${testInfo.file}-${testInfo.project.name}`
    const cached = sessionCache.get(projectName)

    if (cached) {
      await use(cached)
      return
    }

    const requestContext = await playwrightRequest.newContext({
      baseURL: 'http://localhost:5001',
    })
    const data = await callSandbox(requestContext)

    await requestContext.dispose()

    const tempContext = await browser.newContext()
    const tempPage = await tempContext.newPage()

    await doLogin(tempPage, data.user.email)

    const storageStatePath = path.join(
      testInfo.project.outputDir,
      `auth-state-${projectName}.json`
    )
    await tempContext.storageState({ path: storageStatePath })
    await tempContext.close()
    await tempPage.close()

    const session: AuthSession = { data: data, storageStatePath }
    sessionCache.set(projectName, session)
    await use(session)
  },

  authenticatedPage: async ({ browser, authSession }, use, testInfo) => {
    const context = await browser.newContext({
      storageState: authSession.storageStatePath,
      ...testInfo.project.use,
    })
    const page = await context.newPage()

    await use(page)

    await context.close()
  },

  checkAccessibility: async ({ authenticatedPage }, use): Promise<void> => {
    const checkAccessibility = (disabledRules: string[] = []) => {
      return checkAccessibilityHelper(authenticatedPage, disabledRules)
    }

    await use(checkAccessibility)
  },
})

export { expect }
