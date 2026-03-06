import {
  expect,
  type Locator,
  type Page,
  request as playwrightRequest,
} from '@playwright/test'

import { login } from '../helpers/auth'
import { setFeatureFlags } from '../helpers/features'
import {
  BASE_API_URL,
  createProUserEac,
  type ProUserWithOffererAndVenueData,
} from '../helpers/sandbox'

export async function loginAsAndGoToHomepage(
  page: Page,
  getterName: string,
  venueToSelect: string = ''
): Promise<ProUserWithOffererAndVenueData> {
  const requestContext = await playwrightRequest.newContext({
    baseURL: BASE_API_URL,
  })
  const userData = await createProUserEac(requestContext, getterName)
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

const defaultIndividualModulesHidden: Record<IndividualModule, boolean> = {
  HOMOLOGATION_BANNER: false,
  OFFERS_CARD: false,
  STATS_CARD: false,
  EDITO_CARD: false,
  INCOME_CARD: false,
  PARTNER_PAGE_CARD: false,
  NEWSLETTER_CARD: false,
  WEBINARS_CARD: false,
}

export async function expectIndividualModules(
  page: Page,
  visibleModules: IndividualModule[]
) {
  const moduleVisibility = { ...defaultIndividualModulesHidden }
  visibleModules.forEach((module) => {
    moduleVisibility[module] = true
  })

  await expectModuleVisibility(
    page.getByText('Module gestion offres indivs'),
    moduleVisibility.OFFERS_CARD
  )
  await expectModuleVisibility(
    page.getByText('Module statistiques'),
    moduleVisibility.STATS_CARD
  )
  await expectModuleVisibility(
    page.getByText('Module Edito'),
    moduleVisibility.EDITO_CARD
  )

  await expectModuleVisibility(
    page.getByText('Module Budget'),
    moduleVisibility.INCOME_CARD
  )
  await expectModuleVisibility(
    page.getByText('Module page partenaire'),
    moduleVisibility.PARTNER_PAGE_CARD
  )
  await expectModuleVisibility(
    page.getByText('Module Webinaire indiv'),
    moduleVisibility.WEBINARS_CARD
  )
  await expectModuleVisibility(
    page.getByText('Module Newsletter'),
    moduleVisibility.NEWSLETTER_CARD
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

const defaultCollectiveModulesHidden: Record<CollectiveModule, boolean> = {
  HOMOLOGATION_BANNER: false,
  DMS_CARD_TIMELINE: false,
  DMS_CARD_ACCEPTED_BANNER: false,
  COLLECTIVE_OFFER_TEMPLATES_CARD: false,
  COLLECTIVE_OFFERS_CARD: false,
  INCOME_CARD: false,
  ADAGE_PAGE_CARD: false,
  NEWSLETTER_CARD: false,
  WEBINARS_CARD: false,
}

export async function expectCollectiveModules(
  page: Page,
  visibleModules: CollectiveModule[]
) {
  const moduleVisibility = { ...defaultCollectiveModulesHidden }
  visibleModules.forEach((module) => {
    moduleVisibility[module] = true
  })

  await expectModuleVisibility(
    page.getByRole('heading', {
      level: 2,
      name: 'État d’avancement de votre dossier',
    }),
    moduleVisibility.DMS_CARD_TIMELINE
  )

  await expectModuleVisibility(
    page.getByText(/Votre dossier a été validé/),
    moduleVisibility.DMS_CARD_ACCEPTED_BANNER
  )

  await expectModuleVisibility(
    page.getByText('Module gestion offres vitrines'),
    moduleVisibility.COLLECTIVE_OFFER_TEMPLATES_CARD
  )

  await expectModuleVisibility(
    page.getByText('Module gestion offres réservables'),
    moduleVisibility.COLLECTIVE_OFFERS_CARD
  )

  await expectModuleVisibility(
    page.getByText('Module Budget'),
    moduleVisibility.INCOME_CARD
  )

  await expectModuleVisibility(
    page.getByText('Module page partenaire'),
    moduleVisibility.ADAGE_PAGE_CARD
  )

  await expectModuleVisibility(
    page.getByText('Module Newsletter'),
    moduleVisibility.NEWSLETTER_CARD
  )

  await expectModuleVisibility(
    page.getByText('Module Webinaires collectif'),
    moduleVisibility.WEBINARS_CARD
  )
}
