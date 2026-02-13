// biome-ignore assist/source/organizeImports: Unfixable.
import AxeBuilder from '@axe-core/playwright'
import {
  test as base,
  expect,
  request as playwrightRequest,
  type Page,
  type APIRequestContext,
} from '@playwright/test'
import * as path from 'node:path'

import { login } from '../helpers/auth'

export interface AccessibilityResult {
  violations: Array<{
    id: string
    impact: string
    description: string
    nodes: Array<{
      html: string
      target: string[]
    }>
  }>
}

interface AuthSession {
  data: any
  storageStatePath: string
}

const sessionCache = new Map<string, AuthSession>()

export const test = base.extend<{
  callSandbox: (ctx: APIRequestContext) => Promise<any>
  checkAccessibility: (disabledRules?: string[]) => Promise<AccessibilityResult>
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

    await login(tempPage, data.user.email)

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

  checkAccessibility: async ({ authenticatedPage }, use) => {
    const checkAccessibility = async (
      disabledRules: string[] = []
    ): Promise<AccessibilityResult> => {
      const axeBuilder = new AxeBuilder({ page: authenticatedPage })

      if (disabledRules.length > 0) {
        axeBuilder.disableRules(disabledRules)
      }

      const results = await axeBuilder.analyze()

      return {
        violations: results.violations.map((violation) => ({
          id: violation.id,
          impact: violation.impact ?? 'unknown',
          description: violation.description,
          nodes: violation.nodes.map((node) => ({
            html: node.html,
            target: node.target as string[],
          })),
        })),
      }
    }

    await use(checkAccessibility)
  },
})

export { expect }
