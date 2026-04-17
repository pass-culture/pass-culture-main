import { expect, type Page } from '@playwright/test'

const DEFAULT_PASSWORD = 'user@AZERTY123'

export async function doLogin(
  page: Page,
  email: string,
  options?: {
    password?: string
    retry?: boolean
    setCookieConsent?: boolean
  }
): Promise<void> {
  const { password, retry, setCookieConsent } = {
    password: DEFAULT_PASSWORD,
    retry: false,
    setCookieConsent: true,
    ...options,
  }

  if (setCookieConsent) {
    await page.context().addCookies([
      {
        name: 'pc-pro-orejime',
        value: '{"firebase":false,"hotjar":false,"beamer":false,"sentry":true}',
        domain: 'localhost',
        path: '/',
      },
    ])
  }

  await page.goto('/connexion')

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

      return doLogin(page, email, {
        password,
        setCookieConsent,
      })
    }

    throw new Error(`Login failed: ${signinResponse.status()}`)
  }

  await page.waitForResponse((response) =>
    response.url().includes('/offerers/names')
  )
  await page.waitForResponse((response) => response.url().includes('/venues'))

  await expect(page).not.toHaveURL(/\/connexion/)
  await expect(page.getByTestId('spinner')).toHaveCount(0)
}

export async function login(
  page: Page,
  email: string,
  options?: {
    isMultiVenue?: boolean
    password?: string
    setCookieConsent?: boolean
    // TODO (igabriele, 2026-04-16): Delete this prop once `WIP_ENABLE_NEW_PRO_HOME` FF is enabled and removed.
    withNewProHome?: boolean
  }
): Promise<void> {
  const { isMultiVenue, password, setCookieConsent, withNewProHome } = {
    isMultiVenue: false,
    password: DEFAULT_PASSWORD,
    setCookieConsent: true,
    withNewProHome: false,
    ...options,
  }

  await doLogin(page, email, {
    password,
    setCookieConsent,
    retry: true,
  })

  if (isMultiVenue) {
    await expect(page).toHaveURL(/\/hub$/)
    await expect(
      page.getByRole('heading', {
        level: 1,
        name: 'À quelle structure souhaitez-vous accéder ?',
      })
    ).toBeVisible()
  } else {
    await expect(page).toHaveURL(/\/accueil$/)
    await expect(
      page.getByRole('heading', {
        level: 1,
        name: withNewProHome
          ? /^Votre espace /
          : 'Bienvenue sur votre espace partenaire',
      })
    ).toBeVisible()
  }
}

export async function loginAndNavigate(
  page: Page,
  email: string,
  path: string,
  password: string = DEFAULT_PASSWORD,
  setCookieConsent: boolean = true
): Promise<void> {
  await doLogin(page, email, {
    password,
    setCookieConsent,
    retry: true,
  })

  await page.goto(path)

  await expect(page).toHaveURL(new RegExp(path))
  await expect(page.getByTestId('spinner')).toHaveCount(0)
}
