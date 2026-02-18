import * as path from 'node:path'
import {
  test as base,
  expect,
  type Page,
  request as playwrightRequest,
} from '@playwright/test'

import { sandboxCall } from '../helpers/sandbox'

type AdageSandboxData = {
  offerId: number
  offerName: string
  venueName: string
}

interface AdageSession {
  data: AdageSandboxData
  storageStatePath: string
  token: string
}

const sessionCache = new Map<string, AdageSession>()

export const test = base.extend<{
  adageSession: AdageSession
  adagePage: Page
}>({
  adageSession: async ({ browser }, use, testInfo) => {
    const projectName = testInfo.project.name
    const cached = sessionCache.get(projectName)

    if (cached) {
      await use(cached)
      return
    }

    const requestContext = await playwrightRequest.newContext({
      baseURL: 'http://localhost:5001',
    })

    const response = await requestContext.fetch(
      'http://localhost:5001/adage-iframe/testing/token',
      {
        method: 'GET',
      }
    )
    const body = await response.json()

    const data = await sandboxCall<AdageSandboxData>(
      requestContext,
      'GET',
      'http://localhost:5001/sandboxes/pro/create_adage_environment'
    )

    await requestContext.dispose()

    const tempContext = await browser.newContext()
    const tempPage = await tempContext.newPage()

    const storageStatePath = path.join(
      testInfo.project.outputDir,
      `auth-state-${projectName}.json`
    )
    await tempContext.storageState({ path: storageStatePath })
    await tempContext.close()
    await tempPage.close()

    const session: AdageSession = {
      data: data,
      storageStatePath,
      token: body.token,
    }
    sessionCache.set(projectName, session)
    await use(session)
  },
  adagePage: async ({ browser, adageSession }, use, testInfo) => {
    const context = await browser.newContext({
      storageState: adageSession.storageStatePath,
      ...testInfo.project.use,
    })
    const page = await context.newPage()

    await use(page)

    await context.close()
  },
})

export { expect }
