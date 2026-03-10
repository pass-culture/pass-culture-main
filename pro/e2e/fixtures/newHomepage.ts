import {
  type APIRequestContext,
  expect,
  type Locator,
  type Page,
  request as playwrightRequest,
} from '@playwright/test'

import { login } from '../helpers/auth'
import { setFeatureFlags } from '../helpers/features'
import { BASE_API_URL } from '../helpers/sandbox'

export async function loginAsAndGoToHomepage(
  page: Page,
  sandboxSpecificCall: (
    request: APIRequestContext
  ) => Promise<Record<string, any>>,
  venueToSelect: string = ''
): Promise<Record<string, any>> {
  const requestContext = await playwrightRequest.newContext({
    baseURL: BASE_API_URL,
  })
  const userData = await sandboxSpecificCall(requestContext)
  await setFeatureFlags(requestContext, [
    { name: 'WIP_SWITCH_VENUE', isActive: true },
    { name: 'WIP_ENABLE_NEW_PRO_HOME', isActive: true },
  ])
  await requestContext.dispose()

  await login(page, userData.user.email)
  await page.goto('/accueil')

  if (venueToSelect) {
    await page.getByRole('button', { name: venueToSelect }).click()
  }
  return userData
}

function expectModuleVisibility(moduleLocator: Locator, isVisible: boolean) {
  return isVisible
    ? expect.soft(moduleLocator).toBeVisible()
    : expect.soft(moduleLocator).not.toBeVisible()
}

type IndividualModule =
  | 'HOMOLOGATION_BANNER'
  | 'OFFERS_CARD'
  | 'STATS_CARD'
  | 'EDITO_CARD'
  | 'INCOME_CARD'
  | 'PARTNER_PAGE_CARD'
  | 'NEWSLETTER_CARD'
  | 'WEBINARS_CARD'

export async function expectIndividualModules(
  page: Page,
  visibleModules: IndividualModule[]
) {
  await expectModuleVisibility(
    page.getByText('Module gestion offres indivs'),
    visibleModules.includes('OFFERS_CARD')
  )
  await expectModuleVisibility(
    page.getByText('Module statistiques'),
    visibleModules.includes('STATS_CARD')
  )
  await expectModuleVisibility(
    page.getByText('Module Edito'),
    visibleModules.includes('EDITO_CARD')
  )

  await expectModuleVisibility(
    page.getByRole('heading', { level: 3, name: 'Remboursement' }),
    visibleModules.includes('INCOME_CARD')
  )
  await expectModuleVisibility(
    page.getByRole('heading', {
      level: 2,
      name: "Votre page sur l'application",
    }),
    visibleModules.includes('PARTNER_PAGE_CARD')
  )
  await expectModuleVisibility(
    page.getByText('Module Webinaire indiv'),
    visibleModules.includes('WEBINARS_CARD')
  )
  await expectModuleVisibility(
    page.getByText('Module Newsletter'),
    visibleModules.includes('NEWSLETTER_CARD')
  )
}

type CollectiveModule =
  | 'HOMOLOGATION_BANNER'
  | 'DMS_CARD_TIMELINE'
  | 'DMS_CARD_ACCEPTED_BANNER'
  | 'COLLECTIVE_OFFER_TEMPLATES_CARD'
  | 'COLLECTIVE_OFFERS_CARD'
  | 'INCOME_CARD'
  | 'ADAGE_PAGE_CARD'
  | 'NEWSLETTER_CARD'
  | 'WEBINARS_CARD'

export async function expectCollectiveModules(
  page: Page,
  visibleModules: CollectiveModule[]
) {
  await expectModuleVisibility(
    page.getByRole('heading', {
      level: 2,
      name: 'État d’avancement de votre dossier',
    }),
    visibleModules.includes('DMS_CARD_TIMELINE')
  )

  await expectModuleVisibility(
    page.getByText(/Votre dossier a été validé/),
    visibleModules.includes('DMS_CARD_ACCEPTED_BANNER')
  )

  await expectModuleVisibility(
    page.getByText('Module gestion offres vitrines'),
    visibleModules.includes('COLLECTIVE_OFFER_TEMPLATES_CARD')
  )

  await expectModuleVisibility(
    page.getByText('Module gestion offres réservables'),
    visibleModules.includes('COLLECTIVE_OFFERS_CARD')
  )

  await expectModuleVisibility(
    page.getByRole('heading', { level: 3, name: 'Remboursement' }),
    visibleModules.includes('INCOME_CARD')
  )

  await expectModuleVisibility(
    page.getByText('Votre page sur ADAGE'),
    visibleModules.includes('ADAGE_PAGE_CARD')
  )

  await expectModuleVisibility(
    page.getByText('Module Newsletter'),
    visibleModules.includes('NEWSLETTER_CARD')
  )

  await expectModuleVisibility(
    page.getByText('Module Webinaires collectif'),
    visibleModules.includes('WEBINARS_CARD')
  )
}
