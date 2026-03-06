import { expect, test } from '@playwright/test'
import {
  type APIRequestContext,
  request as playwrightRequest,
} from 'playwright-core'

import { setFeatureFlags } from './helpers/features'
import { BASE_API_URL } from './helpers/sandbox'

test.describe('Redirections', () => {
  let requestContext: APIRequestContext
  test.beforeEach(async () => {
    requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
  })
  test.describe('`/` path redirections', () => {
    test('Without WIP_SWITCH_VENUE', async ({ page }) => {
      await page.goto('/')
      await expect(
        page.getByRole('heading', { name: 'Connectez-vous' })
      ).toBeVisible()
    })
    test('With WIP_SWITCH_VENUE', async ({ page }) => {
      await setFeatureFlags(requestContext, [
        {
          name: 'WIP_SWITCH_VENUE',
          isActive: true,
        },
      ])
      await page.goto('/')
      await expect(
        page.getByRole('heading', { name: 'Connectez-vous' })
      ).toBeVisible()
    })
  })
  test.describe('`/inscription` path redirections', () => {
    test('Without WIP_SWITCH_VENUE nor WIP_PRE_SIGNUP_INFO', async ({
      page,
    }) => {
      await setFeatureFlags(requestContext, [
        {
          name: 'WIP_SWITCH_VENUE',
          isActive: false,
        },
        {
          name: 'WIP_PRE_SIGNUP_INFO',
          isActive: false,
        },
      ])
      await page.goto('/inscription')
      await expect(
        page.getByRole('heading', { name: 'Créez votre compte' })
      ).toBeVisible()
    })
    test('With WIP_SWITCH_VENUE and not WIP_PRE_SIGNUP_INFO', async ({
      page,
    }) => {
      await setFeatureFlags(requestContext, [
        {
          name: 'WIP_SWITCH_VENUE',
          isActive: true,
        },
        {
          name: 'WIP_PRE_SIGNUP_INFO',
          isActive: false,
        },
      ])
      await page.goto('/inscription')
      await expect(
        page.getByRole('heading', { name: 'Créez votre compte' })
      ).toBeVisible()
    })
    test.describe('with feature flag WIP_PRE_SIGNUP_INFO', () => {
      test('Without WIP_SWITCH_VENUE', async ({ page }) => {
        await setFeatureFlags(requestContext, [
          {
            name: 'WIP_SWITCH_VENUE',
            isActive: false,
          },
          {
            name: 'WIP_PRE_SIGNUP_INFO',
            isActive: true,
          },
        ])
        await page.goto('/inscription')
        await expect(
          page.getByRole('heading', {
            name: 'Commençons par identifier votre profil',
          })
        ).toBeVisible()
      })
      test('With WIP_SWITCH_VENUE', async ({ page }) => {
        await setFeatureFlags(requestContext, [
          {
            name: 'WIP_SWITCH_VENUE',
            isActive: true,
          },
          {
            name: 'WIP_PRE_SIGNUP_INFO',
            isActive: true,
          },
        ])
        await page.goto('/inscription')
        await expect(
          page.getByRole('heading', {
            name: 'Commençons par identifier votre profil',
          })
        ).toBeVisible()
      })
    })
  })
})
