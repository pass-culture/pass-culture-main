import type { Page } from '@playwright/test'

const DEFAULT_PASSWORD = 'user@AZERTY123'

export async function login(
  page: Page,
  email: string,
  password: string = DEFAULT_PASSWORD
): Promise<void> {
  await page.goto('/connexion')

  await page.context().addCookies([
    {
      name: 'pc-orejime',
      value: '{"firebase":false,"hotjar":false,"beamer":false,"sentry":true}',
      domain: 'localhost',
      path: '/',
    },
  ])

  await page.getByRole('textbox', { name: /adresse email/i }).fill(email)
  await page.getByRole('textbox', { name: /mot de passe/i }).fill(password)

  const [signinResponse] = await Promise.all([
    page.waitForResponse(
      (response) =>
        response.url().includes('/users/signin') &&
        response.request().method() === 'POST'
    ),
    page.getByRole('button', { name: /se connecter/i }).click(),
  ])

  if (!signinResponse.ok()) {
    throw new Error(`Login failed: ${signinResponse.status()}`)
  }

  await page.waitForResponse((response) =>
    response.url().includes('/offerers/names')
  )
}

export async function loginAndNavigate(
  page: Page,
  email: string,
  path: string,
  password: string = DEFAULT_PASSWORD
): Promise<void> {
  await login(page, email, password)

  await page.goto(path)
  await page.waitForLoadState('networkidle')
}
