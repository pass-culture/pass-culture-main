import test, { expect, request as playwrightRequest } from '@playwright/test'

import { login } from './helpers/auth'
import { setFeatureFlags } from './helpers/features'
import {
  BASE_API_URL,
  createProUserWithCollectiveOffers,
  createProUserWithIndividualOffers,
} from './helpers/sandbox'

test.describe('New Homepage', () => {
  test('when I do individual: I should see the individual homepage', async ({
    page,
  }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const userData = await createProUserWithIndividualOffers(requestContext)
    await setFeatureFlags(requestContext, [
      { name: 'WIP_SWITCH_VENUE', isActive: true },
      { name: 'WIP_ENABLE_NEW_PRO_HOME', isActive: true },
    ])
    await requestContext.dispose()

    await login(page, userData.user.email)
    await page.goto('/accueil')

    await page.getByRole('button', { name: /Mon Lieu A/i }).click()

    await expect(
      page.getByRole('heading', {
        level: 1,
        name: 'Votre espace Mon Lieu A',
      })
    ).toBeVisible()

    await expect(page.getByText('Module gestion offres indivs')).toBeVisible()
    await expect(page.getByText('Module statistiques')).toBeVisible()
    await expect(page.getByText('Module Edito')).toBeVisible()

    await expect(page.getByText('Module Budget')).toBeVisible()
    await expect(page.getByText('Module page partenaire')).toBeVisible()
    await expect(page.getByText('Module Webinaire indiv')).toBeVisible()
    await expect(page.getByText('Module Newsletter')).toBeVisible()
  })

  test('when I do collective: I should see the collective homepage', async ({
    page,
  }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const userData = await createProUserWithCollectiveOffers(requestContext)
    await setFeatureFlags(requestContext, [
      { name: 'WIP_SWITCH_VENUE', isActive: true },
      { name: 'WIP_ENABLE_NEW_PRO_HOME', isActive: true },
    ])
    await requestContext.dispose()

    await login(page, userData.user.email)
    await page.goto('/accueil')

    await page.getByRole('button', { name: /Mon Lieu A/i }).click()

    await expect(
      page.getByRole('heading', {
        level: 1,
        name: 'Votre espace Mon Lieu A',
      })
    ).toBeVisible()

    await expect(page.getByText('Module gestion offres vitrines')).toBeVisible()
    await expect(
      page.getByText('Module gestion offres réservables')
    ).toBeVisible()

    await expect(page.getByText('Module Budget')).toBeVisible()
    await expect(page.getByText('Module page partenaire')).toBeVisible()
    await expect(page.getByText('Module Newsletter')).toBeVisible()
  })
})
