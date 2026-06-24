import * as path from 'node:path'
import AxeBuilder from '@axe-core/playwright'
import {
  test as base,
  expect,
  type Page,
  request as playwrightRequest,
} from '@playwright/test'

import { doLogin } from '../helpers/auth'
import {
  BASE_API_URL,
  createProUserWithBookings,
  type DeskBookingsData,
} from '../helpers/sandbox'

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
  data: DeskBookingsData
  storageStatePath: string
}

const sessionCache = new Map<string, AuthSession>()

export const test = base.extend<{
  checkAccessibility: (disabledRules?: string[]) => Promise<AccessibilityResult>
  deskData: DeskBookingsData
  authSession: AuthSession
  authenticatedPage: Page
}>({
  authSession: async ({ browser }, use, testInfo) => {
    const projectName = testInfo.project.name
    const cached = sessionCache.get(projectName)

    if (cached) {
      await use(cached)
      return
    }

    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const deskData = await createProUserWithBookings(requestContext)
    await requestContext.dispose()

    const tempContext = await browser.newContext()
    const tempPage = await tempContext.newPage()
    await doLogin(tempPage, deskData.user.email, { retry: true })

    const storageStatePath = path.join(
      testInfo.project.outputDir,
      `auth-state-${projectName}.json`
    )
    await tempContext.storageState({ path: storageStatePath })
    await tempContext.close()

    const session: AuthSession = { data: deskData, storageStatePath }
    sessionCache.set(projectName, session)
    await use(session)
  },

  deskData: async ({ authSession }, use) => {
    await use(authSession.data)
  },

  authenticatedPage: async ({ browser, authSession }, use, testInfo) => {
    const context = await browser.newContext({
      storageState: authSession.storageStatePath,
      ...testInfo.project.use,
      // Disable CSS animations so axe-core never runs mid-animation.
      // The SnackBar's prefers-reduced-motion block forces opacity:1 immediately,
      // preventing false color-contrast failures.
      reducedMotion: 'reduce',
    })
    const page = await context.newPage()

    await page.goto('/guichet')
    await page.getByLabel('Contremarque').waitFor({ state: 'visible' })

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

      // Wait for CSS animations to finish before running axe-core,
      // otherwise mid-animation transforms can cause false color-contrast failures.
      await authenticatedPage.evaluate(() =>
        Promise.all(document.getAnimations().map((a) => a.finished))
      )

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
