import { expect, request as playwrightRequest, test } from '@playwright/test'

import { expectSuccessSnackbar } from './helpers/assertions'
import { doLogin } from './helpers/auth'
import { setFeatureFlags } from './helpers/features'
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

    const navBar = page.getByRole('navigation', { name: 'Menu principal' })
    await navBar.getByRole('link', { name: 'Paramètres' }).click()
    await expect(page).toHaveURL(/\/parametres\/informations-generales$/)
    await expect(
      page.getByRole('heading', { level: 1, name: 'Paramètres' })
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

    const navBar = page.getByRole('navigation', { name: 'Menu principal' })
    await navBar.getByRole('link', { name: 'Paramètres' }).click()
    await expect(page).toHaveURL(/\/parametres\/informations-generales$/)
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await page.getByRole('link', { name: 'Notifications' }).click()
    await expect(page).toHaveURL(/\/parametres\/notifications$/)

    await page.getByLabel('Adresse email').fill('nouveau@email.com')
    await page.getByRole('button', { name: 'Enregistrer' }).click()

    await expectSuccessSnackbar(page, 'Vos modifications ont été sauvegardées')
    await expect(page).toHaveURL(/\/parametres\/notifications$/)
  })

  test('Leaving with unsaved changes shows the guard dialog and I can quit without saving', async ({
    page,
  }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const userData = await createRegularOnboardedProUser(requestContext)
    await requestContext.dispose()

    await doLogin(page, userData.user.email)
    await navigateToHubAndPickVenue(page, userData.venueName)

    const navBar = page.getByRole('navigation', { name: 'Menu principal' })
    await navBar.getByRole('link', { name: 'Paramètres' }).click()
    await expect(page).toHaveURL(/\/parametres\/informations-generales$/)
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await page.getByRole('link', { name: 'Notifications' }).click()
    await expect(page).toHaveURL(/\/parametres\/notifications$/)

    await page.getByLabel('Adresse email').fill('unsaved@email.com')

    await page.getByRole('link', { name: 'Informations générales' }).click()

    const guardDialog = page.getByRole('dialog', {
      name: 'Des modifications ont été apportées à cette page',
    })
    await expect(guardDialog).toBeVisible()

    await guardDialog
      .getByRole('button', { name: 'Ignorer les modifications' })
      .click()

    await expect(page).toHaveURL(/\/parametres\/informations-generales$/)
    await expect(guardDialog).not.toBeVisible()
  })

  test('Leaving with unsaved changes shows the guard dialog and I can save and quit', async ({
    page,
  }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const userData = await createRegularOnboardedProUser(requestContext)
    await requestContext.dispose()

    await doLogin(page, userData.user.email)
    await navigateToHubAndPickVenue(page, userData.venueName)

    const navBar = page.getByRole('navigation', { name: 'Menu principal' })
    await navBar.getByRole('link', { name: 'Paramètres' }).click()
    await expect(page).toHaveURL(/\/parametres\/informations-generales$/)
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await page.getByRole('link', { name: 'Notifications' }).click()
    await expect(page).toHaveURL(/\/parametres\/notifications$/)

    await page.getByLabel('Adresse email').fill('nouveau@email.com')

    await page.getByRole('link', { name: 'Informations générales' }).click()

    const guardDialog = page.getByRole('dialog', {
      name: 'Des modifications ont été apportées à cette page',
    })
    await expect(guardDialog).toBeVisible()

    await guardDialog
      .getByRole('button', { name: 'Enregistrer et quitter' })
      .click()

    await expectSuccessSnackbar(page, 'Vos modifications ont été sauvegardées')
    await expect(page).toHaveURL(/\/parametres\/informations-generales$/)
    await expect(guardDialog).not.toBeVisible()
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

    const navBar = page.getByRole('navigation', { name: 'Menu principal' })
    await navBar.getByRole('link', { name: 'Paramètres' }).click()
    await expect(page).toHaveURL(/\/parametres\/informations-generales$/)
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await page.getByRole('link', { name: 'Notifications' }).click()
    await expect(page).toHaveURL(/\/parametres\/notifications$/)

    await page.getByLabel('Adresse email').fill('unsaved@email.com')

    await page.getByRole('link', { name: 'Informations générales' }).click()

    const guardDialog = page.getByRole('dialog', {
      name: 'Des modifications ont été apportées à cette page',
    })
    await expect(guardDialog).toBeVisible()

    await guardDialog
      .getByRole('button', { name: 'Fermer la boite de dialogue' })
      .click()

    await expect(page).toHaveURL(/\/parametres\/notifications$/)
    await expect(guardDialog).not.toBeVisible()
  })

  test('Closing a venue requires certification', async ({ page }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const userData = await createRegularOnboardedProUser(requestContext)
    await setFeatureFlags(requestContext, [
      { name: 'WIP_CLOSE_VENUE', isActive: true },
    ])
    await requestContext.dispose()

    await doLogin(page, userData.user.email)
    await navigateToHubAndPickVenue(page, userData.venueName)

    const navBar = page.getByRole('navigation', { name: 'Menu principal' })
    await navBar.getByRole('link', { name: 'Paramètres' }).click()
    await expect(page).toHaveURL(/\/parametres\/informations-generales$/)
    await page.getByRole('link', { name: 'Gestion de la structure' }).click()
    await expect(page).toHaveURL(/\/parametres\/gestion-structure$/)

    await page.getByRole('button', { name: 'Fermer la structure' }).click()

    const closeDialog = page.locator('dialog').filter({
      hasText: 'Vous souhaitez fermer votre structure ?',
    })
    await expect(
      closeDialog.getByRole('heading', {
        name: 'Vous souhaitez fermer votre structure ?',
      })
    ).toBeVisible()
    await expect(
      closeDialog.getByRole('button', {
        name: 'Confirmer la demande de fermeture',
      })
    ).toBeDisabled()
  })

  test('I can close a venue and see that it is disabled afterwards', async ({
    page,
  }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const userData = await createRegularOnboardedProUser(requestContext)
    await setFeatureFlags(requestContext, [
      { name: 'WIP_CLOSE_VENUE', isActive: true },
    ])
    await requestContext.dispose()

    await doLogin(page, userData.user.email)
    await navigateToHubAndPickVenue(page, userData.venueName)

    const navBar = page.getByRole('navigation', { name: 'Menu principal' })
    await navBar.getByRole('link', { name: 'Paramètres' }).click()
    await expect(page).toHaveURL(/\/parametres\/informations-generales$/)
    await page.getByRole('link', { name: 'Gestion de la structure' }).click()
    await expect(page).toHaveURL(/\/parametres\/gestion-structure$/)

    await page.getByRole('button', { name: 'Fermer la structure' }).click()

    const closeDialog = page.locator('dialog').filter({
      hasText: 'Vous souhaitez fermer votre structure ?',
    })
    await expect(
      closeDialog.getByRole('heading', {
        name: 'Vous souhaitez fermer votre structure ?',
      })
    ).toBeVisible()
    await closeDialog.getByRole('checkbox').check()
    await expect(
      closeDialog.getByRole('button', {
        name: 'Confirmer la demande de fermeture',
      })
    ).toBeEnabled()
    await closeDialog
      .getByRole('button', { name: 'Confirmer la demande de fermeture' })
      .click()

    const confirmationDialog = page.locator('dialog').filter({
      hasText: 'Votre demande de fermeture a bien été prise en compte.',
    })
    await expect(
      confirmationDialog.getByRole('heading', {
        name: 'Votre demande de fermeture a bien été prise en compte.',
      })
    ).toBeVisible()
    await confirmationDialog
      .getByRole('button', { name: "J'ai compris" })
      .click()

    await expect(
      page.getByRole('button', { name: 'Fermer la structure' })
    ).toBeDisabled()

    await navBar.getByRole('link', { name: 'Accueil' }).click()
    await expect(page).toHaveURL(/\/accueil$/)
    await expect(page.getByText('Structure fermée')).toBeVisible()
  })
})
