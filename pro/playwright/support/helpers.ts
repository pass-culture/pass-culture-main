import { Page, expect , APIRequestContext, APIResponse } from '@playwright/test'

/**
 * A helper to make API requests to the sandbox, with a built-in retry.
 * @param request The Playwright APIRequestContext object.
 * @param method 'GET' or 'POST'.
 * @param url The full URL for the API endpoint.
 * @param retry A boolean to control the retry mechanism.
 * @returns The APIResponse from the successful call.
 */
export async function sandboxCall(
  request: APIRequestContext,
  method: 'GET' | 'POST',
  url: string,
  retry: boolean = true
): Promise<APIResponse> {
  const options = {
    failOnStatusCode: false,
    timeout: 120 * 1000, // 2 minutes timeout
  }

  const response = await (method === 'GET'
    ? request.get(url, options)
    : request.post(url, options))

  if (response.ok()) {
    return response
  } else if (retry) {
    // eslint-disable-next-line no-console
    console.warn(`Sandbox call to ${url} failed with status ${response.status()}. Retrying in 4s...`)
    await new Promise(resolve => setTimeout(resolve, 4000)) // Wait for 4 seconds
    return sandboxCall(request, method, url, false) // Retry once
  } else {
    throw new Error(`Sandbox call failed for ${method} ${url} with status ${response.status()}: ${await response.text()}`)
  }
}

/**
 * Performs a login action on the application.
 * This is the core login logic, intended to be used by a global setup file.
 * @param page The Playwright page object.
 * @param email The user's email.
 * @param password The user's password.
 */
export async function login(page: Page, email: string) {
  const password = 'user@AZERTY123'

  // Navigate to the login page
  await page.goto('/connexion')
  await page.waitForTimeout(5000)

  // Set the 'orejime' cookie to handle the cookie consent popup
  await page.context().addCookies([
    {
      name: 'orejime',
      value: '{"firebase":true,"hotjar":true,"beamer":true,"sentry":true}',
      domain: 'localhost', // Adjust if your domain is different
      path: '/',
    },
  ])

  // Refresh the page to ensure the cookie is applied
  await page.reload()

  // Wait for connection page title to be visible
  await page.waitForSelector('text=Bienvenue sur l’espace partenaires culturels')

  // Wait for the email input to be ready, then fill credentials and submit
  await expect(page.locator('#email')).toBeEnabled()
  await page.locator('#email').fill(email)
  await page.locator('#password').fill(password)

  // Wait for both the sign-in and subsequent data fetch to complete
  await Promise.all([
    page.waitForResponse(resp => resp.url().includes('/users/signin') && resp.status() === 200),
    page.waitForResponse(resp => resp.url().includes('/offerers/names') && resp.status() === 200),
    page.locator('button[type=submit]').click(),
  ])
}

/**
 * A helper for tests that need to log in and then immediately navigate somewhere.
 * Note: For most cases, using the global setup is preferred.
 * @param page The Playwright page object.
 * @param email The user's email.
 * @param path The path to navigate to after login.
 */
export async function loginAndGoToPage(page: Page, email: string, path: string) {
  await login(page, email)
  await page.goto(path)

  // Wait for page to be stable by checking for spinners
  await expect(page.locator('[data-testid="spinner"]')).not.toBeVisible()
}

/**
 * A helper to log in and land on the didactic onboarding page.
 * @param page The Playwright page object.
 * @param email The user's email.
 */
export async function loginAndSeeDidacticOnboarding(page: Page, email: string) {
  await login(page, email)
  await page.goto('/onboarding')

  // Assertions to verify the page content
  await expect(page.locator('[data-testid="spinner"]')).not.toBeVisible()
  await expect(page.getByText('Bienvenue sur le pass Culture Pro !')).toBeVisible()
  await expect(page.getByText('À qui souhaitez-vous proposer votre première offre ?')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Commencer' })).toHaveCount(2)
}
