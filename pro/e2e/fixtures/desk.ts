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
  createProUserWithBookings,
  type DeskBookingsData,
} from '../helpers/sandbox'

interface AuthSession {
  data: DeskBookingsData
  storageStatePath: string
}

const sessionCache = new Map<string, AuthSession>()

export const test = base.extend<{
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
})

export { expect }
