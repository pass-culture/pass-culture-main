import * as path from 'node:path'
import {
  test as base,
  expect,
  type Page,
  request as playwrightRequest,
} from '@playwright/test'

import { login } from '../helpers/auth'
import { BASE_API_URL, sandboxCall } from '../helpers/sandbox'

export interface ProUserWithCollectiveTemplateOffersResponse {
  user: {
    email: string
  }
  offerPublished: { name: string; venueName: string }
  offerDraft: { name: string; venueName: string }
  offerArchived: { name: string; venueName: string }
  offerUnderReview: { name: string; venueName: string }
  offerRejected: { name: string; venueName: string }
}

interface AuthSession {
  data: ProUserWithCollectiveTemplateOffersResponse
  storageStatePath: string
}

const sessionCache = new Map<string, AuthSession>()

export const test = base.extend<{
  templateOffersData: ProUserWithCollectiveTemplateOffersResponse
  authSession: AuthSession
  page: Page
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
    const data = await sandboxCall<ProUserWithCollectiveTemplateOffersResponse>(
      requestContext,
      'GET',
      `${BASE_API_URL}/sandboxes/pro/create_pro_user_with_collective_offer_templates`
    )
    await requestContext.dispose()

    const tempContext = await browser.newContext()
    const tempPage = await tempContext.newPage()
    await login(tempPage, data.user.email)

    const storageStatePath = path.join(
      testInfo.project.outputDir,
      `auth-state-template-offers-${projectName}.json`
    )
    await tempContext.storageState({ path: storageStatePath })
    await tempContext.close()

    const session: AuthSession = { data, storageStatePath }
    sessionCache.set(projectName, session)
    await use(session)
  },

  templateOffersData: async ({ authSession }, use) => {
    await use(authSession.data)
  },

  page: async ({ browser, authSession }, use, testInfo) => {
    const context = await browser.newContext({
      storageState: authSession.storageStatePath,
      ...testInfo.project.use,
    })
    const page = await context.newPage()

    await page.goto('/offres/vitrines')
    await expect(page.getByTestId('spinner')).toHaveCount(0)
    const filterButton = page.getByRole('button', { name: 'Filtrer' })
    await expect(filterButton).toBeVisible()

    await use(page)

    await context.close()
  },
})

export { expect } from '@playwright/test'
