import test, { expect } from '@playwright/test'

import {
  expectCollectiveModules,
  expectIndividualModules,
  loginAsAndGoToHomepage,
} from './fixtures/newHomepage'

test.describe('when I do individual', () => {
  test('with non draft offers', async ({ page }) => {
    await loginAsAndGoToHomepage(
      page,
      'create_pro_user_with_non_draft_individual_offer'
    )

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

  test('non validated offerer', async ({ page }) => {
    await loginAsAndGoToHomepage(
      page,
      'create_pro_user_with_non_validated_offerer'
    )

    await expect
      .soft(
        page.getByRole('heading', {
          level: 1,
          name: 'Votre espace new_offerer indiv_non_validated_offerer',
        })
      )
      .toBeVisible()
    await expect.soft(page.getByRole('tablist')).not.toBeVisible()

    await expectIndividualModules(page, [
      'HOMOLOGATION_BANNER',
      'OFFERS_CARD',
      'STATS_CARD',
      'EDITO_CARD',
      'INCOME_CARD',
      'PARTNER_PAGE_CARD',
      'NEWSLETTER_CARD',
      'WEBINARS_CARD',
    ])
  })
})

test.describe('when I do collective', () => {
  test('with collective offers', async ({ page }) => {
    await loginAsAndGoToHomepage(
      page,
      'create_pro_user_with_collective_offers',
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
    await loginAsAndGoToHomepage(page, 'create_eac_with_non_validated_offerer')

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
    await loginAsAndGoToHomepage(page, 'create_eac_en_instruction')

    await expect
      .soft(page.getByRole('heading', { level: 1, name: /eac_en_instruction/ }))
      .toBeVisible()
    await expect.soft(page.getByRole('tablist')).not.toBeVisible()

    await expectCollectiveModules(page, ['DMS_CARD_TIMELINE'])
  })

  test('DMS accepted -30d', async ({ page }) => {
    await loginAsAndGoToHomepage(page, 'create_eac_complete_lt_30d')

    await expect
      .soft(page.getByRole('heading', { level: 1, name: /eac_complete_30-d/ }))
      .toBeVisible()
    await expect.soft(page.getByRole('tablist')).not.toBeVisible()

    await expectCollectiveModules(page, [
      'COLLECTIVE_OFFER_TEMPLATES_CARD',
      'COLLECTIVE_OFFERS_CARD',
      'INCOME_CARD',
      'ADAGE_PAGE_CARD',
      'NEWSLETTER_CARD',
      'WEBINARS_CARD',
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
      'create_pro_user_with_individual_offers',
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
      'WEBINARS_CARD',
    ])

    await page.getByRole('tab', { name: 'Collectif' }).click()

    await expectCollectiveModules(page, [
      'COLLECTIVE_OFFER_TEMPLATES_CARD',
      'COLLECTIVE_OFFERS_CARD',
      'INCOME_CARD',
      'ADAGE_PAGE_CARD',
      'NEWSLETTER_CARD',
      'WEBINARS_CARD',
    ])
  })
})
