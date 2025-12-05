import type { APIRequestContext } from '@playwright/test'

const SANDBOX_TIMEOUT = 120000
const RETRY_DELAY = 4000

export async function sandboxCall<T = unknown>(
  request: APIRequestContext,
  method: 'GET' | 'POST',
  url: string,
  retry: boolean = true
): Promise<T> {
  const response = await request.fetch(url, {
    method,
    timeout: SANDBOX_TIMEOUT,
    failOnStatusCode: false,
  })

  if (response.status() === 200) {
    return response.json() as Promise<T>
  }

  if (retry) {
    await new Promise((resolve) => setTimeout(resolve, RETRY_DELAY))
    return sandboxCall<T>(request, method, url, false)
  }

  const body = await response.text()
  throw new Error(
    `Sandbox call failed: ${response.status()} - ${response.statusText()} - ${body}`
  )
}

export interface DeskBookingsData {
  user: {
    email: string
  }
  tokenConfirmed: string
  tokenTooSoon: string
  tokenUsed: string
  tokenCanceled: string
  tokenReimbursed: string
  tokenOther: string
}

export async function createProUserWithBookings(
  request: APIRequestContext
): Promise<DeskBookingsData> {
  return await sandboxCall<DeskBookingsData>(
    request,
    'GET',
    'http://localhost:5001/sandboxes/pro/create_pro_user_with_bookings'
  )
}
