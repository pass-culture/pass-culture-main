import { expect, type Page, test } from '@playwright/test'
import {
  type APIRequestContext,
  request as playwrightRequest,
} from 'playwright-core'

import { checkAccessibility } from './helpers/accessibility'
import { setFeatureFlags } from './helpers/features'
import { BASE_API_URL } from './helpers/sandbox'

async function carouselNavigation(page: Page) {
  await page.goto('/inscription')
  await expect(
    page.getByRole('heading', { name: 'Bienvenue sur pass Culture Pro' })
  ).toBeVisible()

  await page.getByLabel('Partenaire culturel').click()
  await checkAccessibility(page)

  await page.getByRole('button', { name: 'Continuer' }).click()

  await expect(
    page.getByRole('heading', {
      name: 'Deux manières de vous faire connaître',
    })
  ).toBeVisible()
  await checkAccessibility(page)

  await page.getByRole('link', { name: 'Suivant' }).click()

  await expect(
    page.getByRole('heading', {
      name: 'Offres pour les jeunes via l’application',
    })
  ).toBeVisible()
  await checkAccessibility(page)

  await page.getByRole('link', { name: 'Suivant' }).click()

  await expect(
    page.getByRole('heading', {
      name: 'Offres pour les groupes scolaires',
    })
  ).toBeVisible()
  await checkAccessibility(page)

  await page.getByRole('link', { name: 'Suivant' }).click()

  await expect(
    page.getByRole('heading', {
      name: 'Pourquoi rejoindre le pass Culture ?',
    })
  ).toBeVisible()
  await checkAccessibility(page)

  await page.getByRole('link', { name: 'Suivant' }).click()

  await expect(
    page.getByRole('heading', {
      name: 'Comment fonctionne l’inscription ?',
    })
  ).toBeVisible()
  await checkAccessibility(page)

  await page.getByRole('link', { name: 'Démarrer l’inscription' }).click()
}

test.describe('Pre signup pages', () => {
  let requestContext: APIRequestContext
  test.beforeEach(async () => {
    requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
  })
  test('Navigate without WIP_PRE_SIGNUP_SIMULATION', async ({ page }) => {
    await page.context().addCookies([
      {
        name: 'pc-pro-orejime',
        value: '{"firebase":false,"hotjar":false,"beamer":false,"sentry":true}',
        domain: 'localhost',
        path: '/',
      },
    ])
    await setFeatureFlags(requestContext, [
      // DELETE AFTER PR MERGE
      {
        name: 'WIP_PRE_SIGNUP_INFO',
        isActive: true,
      },
      {
        name: 'WIP_PRE_SIGNUP_SIMULATION',
        isActive: false,
      },
    ])
    await carouselNavigation(page)

    await expect(
      page.getByRole('heading', {
        name: 'Créez votre compte',
      })
    ).toBeVisible()
  })

  test('Navigate with WIP_PRE_SIGNUP_SIMULATION', async ({ page }) => {
    await page.context().addCookies([
      {
        name: 'pc-pro-orejime',
        value: '{"firebase":false,"hotjar":false,"beamer":false,"sentry":true}',
        domain: 'localhost',
        path: '/',
      },
    ])
    await setFeatureFlags(requestContext, [
      // DELETE AFTER PR MERGE
      {
        name: 'WIP_PRE_SIGNUP_INFO',
        isActive: true,
      },
      {
        name: 'WIP_PRE_SIGNUP_SIMULATION',
        isActive: true,
      },
    ])
    await carouselNavigation(page)

    await expect(
      page.getByRole('heading', {
        name: 'Renseignez votre SIRET',
      })
    ).toBeVisible()

    await checkAccessibility(page)

    await page.getByRole('link', { name: 'Continuer' }).click()

    await expect(
      page.getByRole('heading', {
        name: 'Quelle est votre activité principale ?',
      })
    ).toBeVisible()

    await checkAccessibility(page)

    await page.getByRole('link', { name: 'Continuer' }).click()

    await expect(
      page.getByRole('heading', {
        name: 'Quels publics souhaitez-vous cibler ?',
      })
    ).toBeVisible()

    await checkAccessibility(page)

    await page.getByRole('link', { name: 'Continuer' }).click()

    await expect(
      page.getByRole('heading', {
        name: 'Voici les justificatifs à préparer pour votre inscription',
      })
    ).toBeVisible()

    await checkAccessibility(page)

    await page.getByRole('link', { name: 'Continuer' }).click()

    await expect(
      page.getByRole('heading', {
        name: 'Créez votre compte',
      })
    ).toBeVisible()
  })
})
