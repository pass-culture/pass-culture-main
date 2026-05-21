import test, { expect, request as playwrightRequest } from '@playwright/test'

import {
  expectCollectiveModules,
  expectIndividualModules,
  loginAsAndGoToHomepage,
} from './fixtures/newHomepage'
import { doLogin } from './helpers/auth'
import {
  BASE_API_URL,
  createEacCompleteLt30d,
  createEacEnInstruction,
  createEacWithNonValidatedOfferer,
  createProUserWithCollectiveOffers,
  createProUserWithIndividualOffers,
  createProUserWithNonDraftIndividualOffer,
  createRegularProUser,
} from './helpers/sandbox'

test.describe('when I do individual', () => {
  test('with non draft offers', async ({ page }) => {
    await loginAsAndGoToHomepage(page, createProUserWithNonDraftIndividualOffer)

    await expect
      .soft(
        page.getByRole('heading', {
          level: 1,
          name: 'Votre espace venue indiv_non_draft_offer',
        })
      )
      .toBeVisible()
    await expect.soft(page.getByRole('tablist')).not.toBeVisible()

    await expectIndividualModules(page, [
      'OFFERS_CARD',
      'STATS_CARD',
      'EDITO_CARD',
      'INCOME_CARD',
      'PARTNER_PAGE_CARD',
      'NEWSLETTER_CARD',
    ])
  })
})

test.describe('when I do collective', () => {
  test('with collective offers', async ({ page }) => {
    await loginAsAndGoToHomepage(
      page,
      createProUserWithCollectiveOffers,
      'Mon Lieu A'
    )

    await expect
      .soft(
        page.getByRole('heading', {
          level: 1,
          name: 'Votre espace Mon Lieu A',
        })
      )
      .toBeVisible()
    await expect.soft(page.getByRole('tablist')).not.toBeVisible()

    await expectCollectiveModules(page, [
      'COLLECTIVE_OFFER_TEMPLATES_CARD',
      'COLLECTIVE_OFFERS_CARD',
      'INCOME_CARD',
      'ADAGE_PAGE_CARD',
      'NEWSLETTER_CARD',
    ])
  })

  test('with non validated offerer', async ({ page }) => {
    await loginAsAndGoToHomepage(page, createEacWithNonValidatedOfferer)

    await expect
      .soft(
        page.getByRole('heading', { level: 1, name: /eac_en_construction/ })
      )
      .toBeVisible()
    await expect.soft(page.getByRole('tablist')).not.toBeVisible()

    await expectCollectiveModules(page, [
      'HOMOLOGATION_BANNER',
      'DMS_CARD_TIMELINE',
    ])
  })

  test('DMS en instruction', async ({ page }) => {
    await loginAsAndGoToHomepage(page, createEacEnInstruction)

    await expect
      .soft(page.getByRole('heading', { level: 1, name: /eac_en_instruction/ }))
      .toBeVisible()
    await expect.soft(page.getByRole('tablist')).not.toBeVisible()

    await expectCollectiveModules(page, ['DMS_CARD_TIMELINE'])
  })

  test('DMS accepted -30d', async ({ page }) => {
    await loginAsAndGoToHomepage(page, createEacCompleteLt30d)

    await expect
      .soft(page.getByRole('heading', { level: 1, name: /eac_complete_30-d/ }))
      .toBeVisible()
    await expect.soft(page.getByRole('tablist')).not.toBeVisible()

    await expectCollectiveModules(page, [
      'COLLECTIVE_OFFERS_CARD',
      'COLLECTIVE_OFFER_TEMPLATES_EMPTY_STATE_CARD',
      'INCOME_CARD',
      'ADAGE_PAGE_CARD',
      'NEWSLETTER_CARD',
      'WEBINAR_CARD',
      'DMS_CARD_ACCEPTED_BANNER',
    ])
  })
})

test.describe('when I do both individual and collective', () => {
  test('I should see tabs and be able to access both homepages', async ({
    page,
  }) => {
    await loginAsAndGoToHomepage(
      page,
      createProUserWithIndividualOffers,
      'Mon Lieu A'
    )

    await expect
      .soft(
        page.getByRole('heading', {
          level: 1,
          name: 'Votre espace Mon Lieu A',
        })
      )
      .toBeVisible()
    await expect.soft(page.getByRole('tablist')).toBeVisible()
    await expect
      .soft(page.getByRole('tab', { name: 'Individuel', selected: true }))
      .toBeVisible()

    await expectIndividualModules(page, [
      'OFFERS_CARD',
      'STATS_CARD',
      'EDITO_CARD',
      'INCOME_CARD',
      'PARTNER_PAGE_CARD',
      'NEWSLETTER_CARD',
      'WEBINAR_CARD',
    ])

    await page.getByRole('tab', { name: 'Collectif' }).click()

    await expectCollectiveModules(page, [
      'COLLECTIVE_OFFER_TEMPLATES_EMPTY_STATE_CARD',
      'COLLECTIVE_OFFERS_EMPTY_STATE_CARD',
      'INCOME_CARD',
      'ADAGE_PAGE_CARD',
      'NEWSLETTER_CARD',
      'WEBINAR_CARD',
    ])
  })
})

test.describe('when I have no offers and no collective access', () => {
  test('should display onboarding offers choice cards', async ({ page }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const userData = await createRegularProUser(requestContext)
    await requestContext.dispose()

    await page.context().addCookies([
      {
        name: 'DID_SKIP_ONBOARDING',
        value: 'true',
        domain: 'localhost',
        path: '/',
      },
    ])

    await doLogin(page, userData.user.email)
    await page.goto('/accueil')
    await expect(page).toHaveURL(/\/accueil$/)

    await expect
      .soft(
        page.getByRole('heading', {
          level: 2,
          name: 'Diffusez votre première offre et pilotez ici votre activité !',
        })
      )
      .toBeVisible()

    await expect
      .soft(
        page.getByRole('heading', {
          name: 'Sur l’application mobile à destination des jeunes',
        })
      )
      .toBeVisible()

    await expect
      .soft(
        page.getByRole('heading', {
          name: 'Sur ADAGE à destination des enseignants',
        })
      )
      .toBeVisible()

    await expect.soft(page.getByRole('tablist')).not.toBeVisible()

    await expect.soft(page.getByText('Je le ferai plus tard')).not.toBeVisible()
  })
})
