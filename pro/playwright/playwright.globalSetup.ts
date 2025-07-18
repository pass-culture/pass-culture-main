/* eslint-disable no-console */

import { request } from '@playwright/test'

export async function waitForApiPath(
  path: string,
  timeout = 60_000,
  interval = 500
): Promise<void> {
  const start = Date.now()
  const api = await request.newContext()
  const url = new URL(path, 'http://localhost:5001').toString()

  while (true) {
    try {
      const res = await api.get(url, { timeout: interval })
      if (res.ok()) {
        return
      }
    } catch (err) {
      console.warn(
        `[Playwright > Setup] Error while checking ${url}: ${(err as Error)?.message}`
      )
    }

    if (Date.now() - start >= timeout) {
      console.error(
        `[Playwright > Setup] Timed out after ${timeout} ms waiting for ${url}`
      )

      process.exit(1)
    }

    await new Promise((resolve) => setTimeout(resolve, interval))
  }
}

// Prevent `Error: apiRequestContext.get: socket hang up` during first run
export default async () => {
  console.info('[Playwright > Setup] Waiting for the API to be healthy...')
  await waitForApiPath('/features')
}
