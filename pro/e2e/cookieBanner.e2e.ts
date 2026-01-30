import {
  expect,
  type Page,
  request as playwrightRequest,
  test,
} from '@playwright/test'

import { loginAndNavigate } from './helpers/auth'
import { BASE_API_URL, createRegularProUser } from './helpers/sandbox'

async function clearBrowserStateAndReload(page: Page): Promise<void> {
  await page.context().clearCookies()
  await page.evaluate(() => {
    localStorage.clear()
    sessionStorage.clear()
  })
  await page.reload()
  await page.waitForLoadState('domcontentloaded')
}

test.describe('Cookie banner', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/connexion')
  })

  test.describe('Cookie management with no login', () => {
    test.beforeEach(async ({ page }) => {
      await clearBrowserStateAndReload(page)
    })

    test('The cookie banner should remain displayed when opening a new page', async ({
      page,
    }) => {
      await expect(page.getByText('Respect de votre vie privée')).toBeVisible()

      await page
        .getByText('Accessibilité : non conforme')
        .click({ force: true })

      await expect(page.getByText('Respect de votre vie privée')).toBeVisible()
    })

    test('I should be able to accept all cookies, and all the cookies are checked in the dialog', async ({
      page,
    }) => {
      await expect(page.getByText('Respect de votre vie privée')).toBeVisible()

      await page.getByRole('button', { name: 'Tout accepter' }).click()

      await expect(
        page.getByText('Respect de votre vie privée')
      ).not.toBeVisible()

      await page
        .getByRole('button', { name: 'Gestion des cookies' })
        .first()
        .click()
      await expect(page.locator('.orejime-Modal')).toBeVisible()

      await expect(
        page.locator('.orejime-Purpose-children .orejime-Purpose-input:checked')
      ).toHaveCount(4)

      await page
        .locator('.orejime-Modal')
        .getByRole('button', { name: 'Enregistrer mes choix' })
        .click()
      await expect(page.locator('.orejime-Modal')).not.toBeVisible()

      await page.getByText('Accessibilité : non conforme').click()

      await expect(
        page.getByText('Respect de votre vie privée')
      ).not.toBeVisible()
    })

    test('I should be able to refuse all cookies, and no cookie is checked in the dialog, except the required', async ({
      page,
    }) => {
      await page
        .getByRole('button', { name: 'Gestion des cookies' })
        .first()
        .click()
      await expect(page.locator('.orejime-Modal')).toBeVisible()

      await page
        .locator('.orejime-Modal')
        .getByRole('button', { name: 'Tout accepter' })
        .click()
      await page
        .locator('.orejime-Modal')
        .getByRole('button', { name: 'Tout refuser' })
        .click()

      await expect(
        page.locator('.orejime-Purpose-children .orejime-Purpose-input:checked')
      ).toHaveCount(1)
    })

    test('I should be able to choose a specific cookie, save and the status should be the same on modal re display', async ({
      page,
    }) => {
      await page
        .getByRole('button', { name: 'Gestion des cookies' })
        .first()
        .click()
      await expect(page.locator('.orejime-Modal')).toBeVisible()

      await expect(page.locator('#orejime-purpose-beamer')).not.toBeChecked()

      await page.locator('.orejime-Modal').getByText('Beamer').click()

      await page
        .locator('.orejime-Modal')
        .getByRole('button', { name: 'Enregistrer mes choix' })
        .click()
      await expect(page.locator('.orejime-Modal')).not.toBeVisible()

      await page
        .getByRole('button', { name: 'Gestion des cookies' })
        .first()
        .click()
      await expect(page.locator('.orejime-Modal')).toBeVisible()

      await expect(page.locator('#orejime-purpose-beamer')).toBeChecked()
    })

    test('I should be able to choose a specific cookie, reload the page and the status should not have been changed', async ({
      page,
    }) => {
      await page
        .getByRole('button', { name: 'Gestion des cookies' })
        .first()
        .click()
      await expect(page.locator('.orejime-Modal')).toBeVisible()

      await expect(page.locator('#orejime-purpose-beamer')).not.toBeChecked()

      await page.locator('.orejime-Modal').getByText('Beamer').click()

      await page.goto('/connexion')

      await expect(page.getByText('Respect de votre vie privée')).toBeVisible()

      await page
        .getByRole('button', { name: 'Gestion des cookies' })
        .first()
        .click()
      await expect(page.locator('.orejime-Modal')).toBeVisible()

      await expect(page.locator('#orejime-purpose-beamer')).not.toBeChecked()
    })

    test('I should be able to choose a specific cookie, close the modal and the status should not have been changed', async ({
      page,
    }) => {
      await expect(page.getByText('Respect de votre vie privée')).toBeVisible()

      await page
        .getByRole('button', { name: 'Gestion des cookies' })
        .first()
        .click()
      await expect(page.locator('.orejime-Modal')).toBeVisible()

      await page.locator('.orejime-Modal').getByText('Beamer').click()

      await page.locator('.orejime-Modal-closeButton').click()
      await expect(page.locator('.orejime-Modal')).not.toBeVisible()

      await page
        .getByRole('button', { name: 'Gestion des cookies' })
        .first()
        .click()
      await expect(page.locator('.orejime-Modal')).toBeVisible()

      await expect(page.locator('#orejime-purpose-beamer')).not.toBeChecked()
    })

    test('I should be able to choose a specific cookie, clear my cookies, and check that specific cookie not checked', async ({
      page,
    }) => {
      await expect(page.getByText('Respect de votre vie privée')).toBeVisible()

      await page
        .getByRole('button', { name: 'Gestion des cookies' })
        .first()
        .click()
      await expect(page.locator('.orejime-Modal')).toBeVisible()

      await page.locator('.orejime-Modal').getByText('Beamer').click()

      await page
        .locator('.orejime-Modal')
        .getByRole('button', { name: 'Enregistrer mes choix' })
        .click()
      await expect(page.locator('.orejime-Modal')).not.toBeVisible()

      await clearBrowserStateAndReload(page)

      await expect(
        page.getByRole('button', { name: 'Gestion des cookies' })
      ).toHaveCount(2)

      await page
        .getByRole('button', { name: 'Gestion des cookies' })
        .first()
        .click()
      await expect(page.locator('.orejime-Modal')).toBeVisible()

      await expect(page.locator('#orejime-purpose-beamer')).not.toBeChecked()
    })
  })

  test.describe('Cookie management with login', () => {
    test('I should be able to choose a specific cookie, log in with another account and check that specific cookie is checked', async ({
      page,
    }) => {
      await clearBrowserStateAndReload(page)

      const requestContext = await playwrightRequest.newContext({
        baseURL: BASE_API_URL,
      })

      const userData = await createRegularProUser(requestContext)
      await requestContext.dispose()

      await loginAndNavigate(
        page,
        userData.user.email,
        '/accueil',
        undefined,
        false
      )

      await page
        .getByRole('button', { name: 'Gestion des cookies' })
        .first()
        .click()
      await expect(page.locator('.orejime-Modal')).toBeVisible()

      await page.locator('.orejime-Modal').getByText('Beamer').click()

      await page
        .locator('.orejime-Modal')
        .getByRole('button', { name: 'Enregistrer mes choix' })
        .click()
      await expect(page.locator('.orejime-Modal')).not.toBeVisible()

      await page.getByTestId('profile-button').click()
      await expect(page.getByTestId('header-dropdown-menu-div')).toBeVisible()
      await page.getByText('Se déconnecter').click()
      await expect(page).toHaveURL(/\/connexion/)

      const newUserData = await playwrightRequest
        .newContext({ baseURL: BASE_API_URL })
        .then(async (ctx) => {
          const data = await createRegularProUser(ctx)
          await ctx.dispose()
          return data
        })

      await loginAndNavigate(
        page,
        newUserData.user.email,
        '/accueil',
        undefined,
        false
      )

      await page
        .getByRole('button', { name: 'Gestion des cookies' })
        .first()
        .click()
      await expect(page.locator('.orejime-Modal')).toBeVisible()

      await expect(page.locator('#orejime-purpose-beamer')).toBeChecked()
    })
  })
})
