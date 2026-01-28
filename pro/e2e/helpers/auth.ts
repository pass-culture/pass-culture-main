import { expect, type Page } from '@playwright/test'

const DEFAULT_PASSWORD = 'user@AZERTY123'

async function doLogin(
  page: Page,
  email: string,
  password: string,
  setCookieConsent: boolean,
  retry: boolean = true
): Promise<void> {
  await page.goto('/connexion')

  if (setCookieConsent) {
    await page.context().addCookies([
      {
        name: 'pc-orejime',
        value: '{"firebase":false,"hotjar":false,"beamer":false,"sentry":true}',
        domain: 'localhost',
        path: '/',
      },
    ])
  }

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
    if (retry) {
      await page.waitForTimeout(5000)
      return doLogin(page, email, password, setCookieConsent, false)
    }
    throw new Error(`Login failed: ${signinResponse.status()}`)
  }

  await page.waitForResponse((response) =>
    response.url().includes('/offerers/names')
  )
  await page.waitForResponse((response) => response.url().includes('/venues'))

  await page.waitForURL((url) => !url.pathname.includes('/connexion'))
}

export async function login(
  page: Page,
  email: string,
  password: string = DEFAULT_PASSWORD,
  setCookieConsent: boolean = true
): Promise<void> {
  await doLogin(page, email, password, setCookieConsent, true)
}

export async function loginAndNavigate(
  page: Page,
  email: string,
  path: string,
  password: string = DEFAULT_PASSWORD,
  setCookieConsent: boolean = true
): Promise<void> {
  await login(page, email, password, setCookieConsent)

  await page.goto(path)

  if (path === '/accueil') {
    await expect(page.getByTestId('spinner')).not.toBeVisible()
    await expect(
      page.getByText('Bienvenue sur votre espace partenaire')
    ).toBeVisible()
  } else {
    await expect(page).toHaveURL(new RegExp(path))
    await expect(page.getByTestId('spinner')).not.toBeVisible()
  }
}
