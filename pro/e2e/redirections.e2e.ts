import { expect, request, test } from '@playwright/test'

import { doLogin, login } from './helpers/auth'
import {
  goBackToHub,
  navigateToAdministrationSpace,
} from './helpers/navigation'
import {
  BASE_API_URL,
  createNewProUser,
  createProUserWithFinancialDataAnd3Venues,
  createProUserWithNonValidatedOfferer,
  createRegularOnboardedProUser,
  createRegularProUserWithBothAttachedAndNonAttachedOfferers,
} from './helpers/sandbox'

test.describe('Redirections', () => {
  test('`/` path redirections', async ({ page }) => {
    await page.goto('/')
    await expect(
      page.getByRole('heading', { name: 'Connectez-vous' })
    ).toBeVisible()
  })
  test('`/inscription` path redirections', async ({ page }) => {
    await page.goto('/inscription')
    await expect(
      page.getByRole('heading', {
        name: 'Commençons par identifier votre profil',
      })
    ).toBeVisible()
  })
  test('No structure : should add a new structure', async ({ page }) => {
    const requestContext = await request.newContext({
      baseURL: BASE_API_URL,
    })

    const userData = await createNewProUser(requestContext)
    await requestContext.dispose()
    await doLogin(page, userData.user.email, { retry: true })
    await page.goto('/')
    await expect(
      page.getByText('Dites-nous pour quelle structure vous travaillez')
    ).toBeVisible()
  })
  test('1 venue and is onboarded : should redirect to /accueil and have full access', async ({
    page,
  }) => {
    const requestContext = await request.newContext({
      baseURL: BASE_API_URL,
    })

    const userData = await createRegularOnboardedProUser(requestContext)
    await requestContext.dispose()
    await login(page, userData.user.email)

    await page.goto('/')
    await expect(page).toHaveURL('/accueil')
    await expect(page.getByText('Votre espace')).toBeVisible()

    await goBackToHub(page)
    await expect(
      page.getByText('À quelle structure souhaitez-vous accéder ?')
    ).toBeVisible()

    await navigateToAdministrationSpace(page)
    await expect(
      page.getByRole('heading', { level: 1, name: 'Gestion financière' })
    ).toBeVisible()
  })
  test('Multiple venues and onboarded : should redirect to /hub and have full access', async ({
    page,
  }) => {
    const requestContext = await request.newContext({
      baseURL: BASE_API_URL,
    })

    const userData =
      await createProUserWithFinancialDataAnd3Venues(requestContext)
    await requestContext.dispose()
    await doLogin(page, userData.user.email, { retry: true })

    await page.goto('/')
    await expect(
      page.getByText('À quelle structure souhaitez-vous accéder ?')
    ).toBeVisible()

    const venueButton = page.getByRole('button', { name: 'Mon Lieu 1' }).last()

    await expect(venueButton).toBeVisible()
    await venueButton.click()
    await expect(page.getByText('Votre espace')).toBeVisible()

    await navigateToAdministrationSpace(page)
    await expect(
      page.getByRole('heading', { level: 1, name: 'Gestion financière' })
    ).toBeVisible()
  })
  test('1 venue non attached : should redirect to /rattachement-en-cours and have hub & admin access', async ({
    page,
  }) => {
    const requestContext = await request.newContext({
      baseURL: BASE_API_URL,
    })

    const userData = await createProUserWithNonValidatedOfferer(requestContext)
    await requestContext.dispose()

    await doLogin(page, userData.user.email)

    await page.goto('/')
    await expect(page).toHaveURL('/rattachement-en-cours')
    await expect(
      page.getByText(
        'Votre rattachement est en cours de traitement par les équipes du pass Culture'
      )
    ).toBeVisible()
    await goBackToHub(page)
    await expect(
      page.getByText('À quelle structure souhaitez-vous accéder ?')
    ).toBeVisible()
    await navigateToAdministrationSpace(page)
    await expect(
      page.getByRole('heading', { level: 1, name: 'Gestion financière' })
    ).toBeVisible()
  })
  test('Multiple venues attached and non-attached : should redirect to hub and have access depending on selected venue', async ({
    page,
  }) => {
    const requestContext = await request.newContext({
      baseURL: BASE_API_URL,
    })

    const userData =
      await createRegularProUserWithBothAttachedAndNonAttachedOfferers(
        requestContext
      )
    await requestContext.dispose()
    await doLogin(page, userData.user.email, { retry: true })
    await page.goto('/')
    await expect(page).toHaveURL('/hub')
    await expect(
      page.getByText('À quelle structure souhaitez-vous accéder ?')
    ).toBeVisible()

    const venueButtonAttached = page
      .getByRole('button', { name: 'Mon Lieu' })
      .first()

    await expect(venueButtonAttached).toBeVisible()
    await venueButtonAttached.click()
    await expect(page).toHaveURL('/accueil')
    await expect(page.getByText('Votre espace')).toBeVisible()

    await goBackToHub(page)
    const venueButtonNonAttached = page
      .getByRole('button', { name: 'Mon Lieu non rattaché' })
      .last()

    await expect(venueButtonNonAttached).toBeVisible()
    await venueButtonNonAttached.click()
    await expect(page).toHaveURL('/rattachement-en-cours')
    await expect(
      page.getByText(
        'Votre rattachement est en cours de traitement par les équipes du pass Culture'
      )
    ).toBeVisible()
  })
})
