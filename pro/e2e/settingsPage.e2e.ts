import { expect, request as playwrightRequest, test } from '@playwright/test'

import { expectSuccessSnackbar } from './helpers/assertions'
import { doLogin } from './helpers/auth'
import { navigateToHubAndPickVenue } from './helpers/navigation'
import { BASE_API_URL, createRegularOnboardedProUser } from './helpers/sandbox'

test.describe('Settings page', () => {
  test('I can navigate between the 3 tabs', async ({ page }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const userData = await createRegularOnboardedProUser(requestContext)
    await requestContext.dispose()

    await doLogin(page, userData.user.email)
    await navigateToHubAndPickVenue(page, userData.venueName)

    await page.getByRole('link', { name: 'Paramètres généraux' }).click()
    await expect(page).toHaveURL(/\/parametres\/informations-generales$/)
    await expect(
      page.getByRole('heading', { level: 1, name: 'Paramètres généraux' })
    ).toBeVisible()
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await page.getByRole('link', { name: 'Notifications' }).click()
    await expect(page).toHaveURL(/\/parametres\/notifications$/)
    await expect(
      page.getByRole('heading', { name: 'Notifications de réservations' })
    ).toBeVisible()

    await page.getByRole('link', { name: 'Synchronisations' }).click()
    await expect(page).toHaveURL(/\/parametres\/synchronisations$/)
    await expect(
      page.getByRole('heading', { name: 'Gestion des synchronisations' })
    ).toBeVisible()

    await page.getByRole('link', { name: 'Informations générales' }).click()
    await expect(page).toHaveURL(/\/parametres\/informations-generales$/)
  })

  test('Saving shows a success toaster and keeps me on the page', async ({
    page,
  }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const userData = await createRegularOnboardedProUser(requestContext)
    await requestContext.dispose()

    await doLogin(page, userData.user.email)
    await navigateToHubAndPickVenue(page, userData.venueName)

    await page.getByRole('link', { name: 'Paramètres généraux' }).click()
    await expect(page).toHaveURL(/\/parametres\/informations-generales$/)
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await page.getByRole('link', { name: 'Notifications' }).click()
    await expect(page).toHaveURL(/\/parametres\/notifications$/)

    await page.getByLabel('Adresse email').fill('nouveau@email.com')
    await page.getByRole('button', { name: 'Enregistrer' }).click()

    await expectSuccessSnackbar(page, 'Vos modifications ont été sauvegardées')
    await expect(page).toHaveURL(/\/parametres\/notifications$/)
  })

  test('Leaving with unsaved changes shows the guard dialog and I can quit', async ({
    page,
  }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const userData = await createRegularOnboardedProUser(requestContext)
    await requestContext.dispose()

    await doLogin(page, userData.user.email)
    await navigateToHubAndPickVenue(page, userData.venueName)

    await page.getByRole('link', { name: 'Paramètres généraux' }).click()
    await expect(page).toHaveURL(/\/parametres\/informations-generales$/)
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await page.getByRole('link', { name: 'Notifications' }).click()
    await expect(page).toHaveURL(/\/parametres\/notifications$/)

    await page.getByLabel('Adresse email').fill('unsaved@email.com')

    await page.getByRole('link', { name: 'Informations générales' }).click()

    await expect(
      page.getByText('Les informations non enregistrées seront perdues')
    ).toBeVisible()

    await page.getByRole('button', { name: 'Quitter la page' }).click()

    await expect(page).toHaveURL(/\/parametres\/informations-generales$/)
    await expect(
      page.getByText('Les informations non enregistrées seront perdues')
    ).not.toBeVisible()
  })

  test('Leaving with unsaved changes shows the guard dialog and I can stay', async ({
    page,
  }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const userData = await createRegularOnboardedProUser(requestContext)
    await requestContext.dispose()

    await doLogin(page, userData.user.email)
    await navigateToHubAndPickVenue(page, userData.venueName)

    await page.getByRole('link', { name: 'Paramètres généraux' }).click()
    await expect(page).toHaveURL(/\/parametres\/informations-generales$/)
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await page.getByRole('link', { name: 'Notifications' }).click()
    await expect(page).toHaveURL(/\/parametres\/notifications$/)

    await page.getByLabel('Adresse email').fill('unsaved@email.com')

    await page.getByRole('link', { name: 'Informations générales' }).click()

    await expect(
      page.getByText('Les informations non enregistrées seront perdues')
    ).toBeVisible()

    await page.getByRole('button', { name: 'Rester sur la page' }).click()

    await expect(page).toHaveURL(/\/parametres\/notifications$/)
    await expect(
      page.getByText('Les informations non enregistrées seront perdues')
    ).not.toBeVisible()
  })
})
