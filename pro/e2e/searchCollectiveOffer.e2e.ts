import { addWeeks, format } from 'date-fns'

import {
  type CollectiveOffersUserData,
  expect,
  test,
} from './fixtures/searchCollectiveOffer'
import { checkAccessibility } from './helpers/accessibility'
import { expectCollectiveOffersAreFound } from './helpers/assertions'

const INSTITUTION_NAME = 'COLLEGE 123'
const FORMAT_NAME = 'Concert'

const BOOKABLE_OFFERS_COLUMNS = [
  '',
  'Nom de l’offre',
  'Dates',
  'Prix et participants',
  'Établissement',
  'Localisation',
  'Statut',
]

function collectiveFormatEventDate(date: string): string {
  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    timeZone: 'Europe/Paris',
  }).format(new Date(date))
}

function getPublishedCollectiveOfferRow(
  userData: CollectiveOffersUserData
): string[] {
  const { offerPublished } = userData
  return [
    '',
    offerPublished.name,
    `Du ${collectiveFormatEventDate(offerPublished.startDatetime)}au ${collectiveFormatEventDate(offerPublished.endDatetime)}`,
    '100€25 participants',
    INSTITUTION_NAME,
    'À déterminer',
    'publiée',
  ]
}

test.describe('Search collective offers', () => {
  test.beforeEach(async ({ authenticatedPage: page }) => {
    await page.goto('/offres/collectives')
    await expect(page.getByTestId('spinner')).toHaveCount(0)
    await expect(page.getByText('Filtrer')).toBeVisible()
  })

  test('I should be able to search with a name and see expected results', async ({
    authenticatedPage: page,
    collectiveOffersUserData: userData,
  }) => {
    await checkAccessibility(page)

    await page.getByLabel('Nom de l’offre').fill(userData.offerPublished.name)

    const responsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/bookable-offers') &&
        response.request().method() === 'GET'
    )
    await page.getByText('Rechercher').click()
    const response = await responsePromise
    expect(response.status()).toBe(200)

    await expectCollectiveOffersAreFound(page, [
      BOOKABLE_OFFERS_COLUMNS,
      getPublishedCollectiveOfferRow(userData),
    ])
  })

  test('I should be able to search with a location and see expected results', async ({
    authenticatedPage: page,
    collectiveOffersUserData: userData,
  }) => {
    await page.getByText('Filtrer').click()
    await page
      .getByLabel('Localisation')
      .selectOption('En établissement scolaire')

    const responsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/bookable-offers') &&
        response.request().method() === 'GET'
    )
    await page.getByText('Rechercher').click()
    const response = await responsePromise
    expect(response.status()).toBe(200)

    await expectCollectiveOffersAreFound(page, [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        userData.offerArchived.name,
        '-',
        '-',
        'DE LA TOUR',
        "Dans l'établissement",
        'archivée',
      ],
    ])
  })

  test(`I should be able to search with a format "${FORMAT_NAME}" and see expected results`, async ({
    authenticatedPage: page,
    collectiveOffersUserData: userData,
  }) => {
    await page.getByText('Filtrer').click()
    await page.getByLabel('Format').selectOption(FORMAT_NAME)

    const responsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/bookable-offers') &&
        response.request().method() === 'GET'
    )
    await page.getByText('Rechercher').click()
    const response = await responsePromise
    expect(response.status()).toBe(200)

    await expectCollectiveOffersAreFound(page, [
      BOOKABLE_OFFERS_COLUMNS,
      getPublishedCollectiveOfferRow(userData),
    ])
  })

  test('I should be able to search with a Date and see expected results', async ({
    authenticatedPage: page,
    collectiveOffersUserData: userData,
  }) => {
    await page.getByText('Filtrer').click()

    const dateSearch = format(addWeeks(new Date(), 2), 'yyyy-MM-dd')
    await page.getByLabel('Début de la période').fill(dateSearch)
    await page.getByLabel('Fin de la période').fill(dateSearch)

    const responsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/bookable-offers') &&
        response.request().method() === 'GET'
    )
    await page.getByText('Rechercher').click()
    const response = await responsePromise
    expect(response.status()).toBe(200)

    await expectCollectiveOffersAreFound(page, [
      BOOKABLE_OFFERS_COLUMNS,
      getPublishedCollectiveOfferRow(userData),
    ])
  })

  test('I should be able to search with a status "Publiée" and see expected results', async ({
    authenticatedPage: page,
    collectiveOffersUserData: userData,
  }) => {
    await page.getByText('Filtrer').click()

    await page.getByRole('button', { name: 'Statut' }).click()
    await page.getByText('Publiée sur ADAGE').click()
    await page.getByRole('heading', { name: 'Offres réservables' }).click()

    const responsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/bookable-offers') &&
        response.request().method() === 'GET'
    )
    await page.getByText('Rechercher').click()
    const response = await responsePromise
    expect(response.status()).toBe(200)

    await expectCollectiveOffersAreFound(page, [
      BOOKABLE_OFFERS_COLUMNS,
      getPublishedCollectiveOfferRow(userData),
    ])
  })

  test('I should be able to search with several filters and see expected results, then reinit filters', async ({
    authenticatedPage: page,
    collectiveOffersUserData: userData,
  }) => {
    await page.getByText('Filtrer').click()

    await page.getByLabel('Localisation').selectOption('À déterminer')
    await page.getByLabel('Format').selectOption('Représentation')
    await page.getByLabel('Nom de l’offre').fill('brouillon')

    await page.getByRole('button', { name: 'Statut' }).click()
    const panelScrollable = page.getByTestId('panel-scrollable')
    await panelScrollable.evaluate((el) => {
      el.scrollTop = el.scrollHeight
    })
    await panelScrollable.getByLabel('Brouillon').click()
    await page.getByRole('heading', { name: 'Offres réservables' }).click()

    let responsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/bookable-offers') &&
        response.request().method() === 'GET'
    )
    await page.getByText('Rechercher').click()
    await responsePromise

    await expectCollectiveOffersAreFound(page, [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        userData.offerDraft.name,
        '-',
        '-',
        'DE LA TOUR',
        'À déterminer',
        'brouillon',
      ],
    ])

    await page.getByText('Réinitialiser les filtres').click()

    await page.getByRole('button', { name: 'Statut' }).click()
    await expect(page.getByText('En instruction')).not.toBeChecked()
    await expect(
      page.getByRole('combobox', { name: /Localisation/ })
    ).toHaveValue('all')
    await expect(page.getByRole('combobox', { name: /Format/ })).toHaveValue(
      'all'
    )

    await page.getByLabel('Nom de l’offre').clear()

    responsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/bookable-offers') &&
        response.request().method() === 'GET'
    )
    await page.getByText('Rechercher').click()
    await responsePromise

    const rows = page.locator('tbody').locator('tr[data-testid="table-row"]')
    await expect(rows).toHaveCount(5)
  })

  test('I should be able to download offers in CSV and Excel format', async ({
    authenticatedPage: page,
  }) => {
    await page.getByText('Télécharger').click()

    const csvResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/offers/csv') &&
        response.request().method() === 'GET'
    )
    await page.getByText('Télécharger format CSV').click()
    const csvResponse = await csvResponsePromise
    expect(csvResponse.status()).toBe(200)

    const excelResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/offers/excel') &&
        response.request().method() === 'GET'
    )
    await page.getByText('Télécharger format Excel').click()
    const excelResponse = await excelResponsePromise
    expect(excelResponse.status()).toBe(200)
  })
})
