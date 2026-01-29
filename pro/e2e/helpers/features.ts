import { expect, type request as playwrightRequest } from '@playwright/test'

import { BASE_API_URL } from './sandbox'

export interface Feature {
  name: string
  isActive: boolean
}

export async function setFeatureFlags(
  requestContext: Awaited<ReturnType<typeof playwrightRequest.newContext>>,
  features: Feature[]
): Promise<void> {
  const response = await requestContext.patch(
    `${BASE_API_URL}/testing/features`,
    {
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      data: { features },
    }
  )
  expect(response.status()).toBe(204)
}
