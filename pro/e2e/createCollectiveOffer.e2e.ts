import type { Page } from '@playwright/test'
import { addDays, format } from 'date-fns'
import type { Response } from 'playwright-core'

import {
  BOOKABLE_OFFERS_COLUMNS,
  TEMPLATE_OFFERS_COLUMNS,
} from './common/constants'
import { expect, test } from './fixtures/createCollectiveOffer'
import type { AccessibilityResult } from './fixtures/desk'
import {
  autoCompleteAddress,
  fillCustomAddress,
  mockAddressSearch,
} from './helpers/address'
import { expectCollectiveOffersAreFound } from './helpers/assertions'
import {
  isGetCollectiveOffersBookableResponse,
  isGetCollectiveOffersTemplateResponse,
  isGetDomainsResponse,
  isGetInstitutionalRedactorsResponse,
  isGetVenuesReponse,
  isPostCollectiveStocksResponse,
} from './helpers/requests'

const newOfferName = 'Ma nouvelle offre collective créée'
const otherVenueName = 'Mon Lieu 2'
const venueName = 'Mon Lieu 1'
const venueFullAddress = '1 boulevard Poissonnière, 75002, Paris'
const defaultDate = addDays(new Date(), 2)
const defaultBookingLimitDate = addDays(new Date(), 1)

const commonOfferData = {
  title: newOfferName,
  description: 'Bookable draft offer',
  email: 'example@passculture.app', // gitleaks:ignore
  date: defaultDate,
  bookingLimitDate: defaultBookingLimitDate,
  time: '18:30',
  participants: '10',
  price: '10',
  priceDescription: 'description',
  institution: 'COLLEGE 123',
}

test.describe('Create collective offers', () => {
  test.beforeEach(async ({ authenticatedPage: page }) => {
    await page.goto('/offre/creation')
    await mockAddressSearch(page)
  })

  test('Create collective bookable offers with a precise address (the venue address, selected by default)', async ({
    authenticatedPage: page,
    checkAccessibility,
  }) => {
    await checkAccessibility()
    await fillBasicOFferForm(page)
    await fillOfferDetails(page, checkAccessibility)
    await fillDatesAndPrice(page, checkAccessibility)
    await fillInstitution(page, checkAccessibility)
    await expect(page.getByText(`Adresse : ${venueFullAddress}`)).toBeVisible()
    await publishAndSearchOffer(page, checkAccessibility)

    await expectCollectiveOffersAreFound(page, [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        `N°6${newOfferName}`,
        format(commonOfferData.date, 'dd/MM/yyyy'),
        '10€',
        'COLLEGE 123 75000',
        `${venueName} - 1 boulevard Poissonnière 75002 Paris`,
        'publiée',
      ],
    ])
  })

  test('Create collective bookable offers with a precise address (another address)', async ({
    authenticatedPage: page,
    checkAccessibility,
  }) => {
    await fillBasicOFferForm(page)

    await page.getByLabel('Autre adresse').click()
    await autoCompleteAddress(page)
    await fillOfferDetails(page, checkAccessibility)
    await fillDatesAndPrice(page, checkAccessibility)
    await fillInstitution(page, checkAccessibility)
    await expect(
      page.getByText('Adresse : 3 RUE DE VALOIS, 75008, Paris')
    ).toBeVisible()
    await publishAndSearchOffer(page, checkAccessibility)

    await expectCollectiveOffersAreFound(page, [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        `N°7${newOfferName}`,
        `${format(commonOfferData.date, 'dd/MM/yyyy')}`,
        '10€',
        'COLLEGE 123 75000',
        '3 RUE DE VALOIS 75008 Paris',
        'publiée',
      ],
      [],
    ])
  })

  test('Create collective bookable offers with a precise address (another address - manual entry)', async ({
    authenticatedPage: page,
    checkAccessibility,
  }) => {
    await fillBasicOFferForm(page)
    await page.getByLabel('Autre adresse').click()
    await fillCustomAddress(page, expect)
    await fillOfferDetails(page, checkAccessibility)
    await fillDatesAndPrice(page, checkAccessibility)
    await fillInstitution(page, checkAccessibility)
    await expect(
      page.getByText('Intitulé : Libellé de mon adresse custom')
    ).toBeVisible()
    await expect(
      page.getByText('Adresse : Place de la gare, 12312, Y')
    ).toBeVisible()
    await publishAndSearchOffer(page, checkAccessibility)

    await expectCollectiveOffersAreFound(page, [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        `N°8${newOfferName}`,
        `${format(commonOfferData.date, 'dd/MM/yyyy')}`,
        '10€',
        'COLLEGE 123 75000',
        'Libellé de mon adresse custom - Place de la gare 12312 Y',
        'publiée',
      ],
      [],
      [],
    ])
  })

  test('Create collective bookable offers with school location', async ({
    authenticatedPage: page,
    checkAccessibility,
  }) => {
    await fillBasicOFferForm(page)
    await page.getByLabel('En établissement scolaire').click()
    await fillOfferDetails(page, checkAccessibility)
    await fillDatesAndPrice(page, checkAccessibility)
    await fillInstitution(page, checkAccessibility)
    await expect(page.getByText('Dans l’établissement scolaire')).toBeVisible()
    await expect(
      page.getByText('Zone de mobilité : Paris (75) - Hauts-de-Seine (92)')
    ).toBeVisible()
    await publishAndSearchOffer(page, checkAccessibility)

    await expectCollectiveOffersAreFound(page, [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        `N°9${newOfferName}`,
        `${format(commonOfferData.date, 'dd/MM/yyyy')}`,
        '10€',
        'COLLEGE 123 75000',
        "Dans l'établissement",
        'publiée',
      ],
      [],
      [],
      [],
    ])
  })

  test('Create collective bookable offers with to be defined location', async ({
    authenticatedPage: page,
    checkAccessibility,
  }) => {
    await fillBasicOFferForm(page)
    await page.getByLabel('À déterminer avec l’enseignant').click()
    await page.getByLabel('Commentaire').fill('Test commentaire')
    await fillOfferDetails(page, checkAccessibility)
    await fillDatesAndPrice(page, checkAccessibility)
    await fillInstitution(page, checkAccessibility)
    await expect(page.getByText('À déterminer avec l’enseignant')).toBeVisible()
    await expect(page.getByText('Commentaire : Test commentaire')).toBeVisible()
    await expect(
      page.getByText('Zone de mobilité : Paris (75) - Hauts-de-Seine (92)')
    ).toBeVisible()
    await publishAndSearchOffer(page, checkAccessibility)

    await expectCollectiveOffersAreFound(page, [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        `N°10${newOfferName}`,
        `${format(commonOfferData.date, 'dd/MM/yyyy')}`,
        '10€',
        'COLLEGE 123 75000',
        'À déterminer',
        'publiée',
      ],
      [],
      [],
      [],
      [],
    ])
  })

  test('Create collective offer template and use it in duplication page', async ({
    authenticatedPage: page,
    checkAccessibility,
  }) => {
    await page.getByLabel('Une offre vitrine').first().click()
    await page.getByText('Étape suivante').click()
    await fillBasicOFferForm(page)
    await fillOfferDetails(page, checkAccessibility, true)
    await expect(page.getByText('Intitulé : Mon Lieu 1')).toBeVisible()
    await expect(page.getByText(`Adresse : ${venueFullAddress}`)).toBeVisible()
    await publishAndSearchOffer(
      page,
      checkAccessibility,
      isGetCollectiveOffersTemplateResponse
    )

    await expectCollectiveOffersAreFound(page, [
      TEMPLATE_OFFERS_COLUMNS,
      [
        '',
        `Offre vitrine${commonOfferData.title}`,
        'Toute l’année scolaire',
        `${venueName} - 1 boulevard Poissonnière 75002 Paris`,
        'publiée',
      ],
    ])
  })

  test('Create collective bookable offers with a precise address (the venue address, selected by default) and update location', async ({
    authenticatedPage: page,
    checkAccessibility,
  }) => {
    await fillBasicOFferForm(page)
    await fillOfferDetails(page, checkAccessibility)
    await fillDatesAndPrice(page, checkAccessibility)
    await fillInstitution(page, checkAccessibility)
    await publishAndSearchOffer(page, checkAccessibility)

    await page.getByRole('link', { name: `N°6 ${newOfferName}` }).click()
    await page.getByLabel('Modifier').first().click()
    await page.getByLabel('Autre adresse').click()
    await autoCompleteAddress(page)
    await page
      .getByLabel('Intitulé de la localisation')
      .fill('Libellé de mon adresse custom')
    await page.getByText('Enregistrer et continuer').click()
    await expect(
      page.getByText(
        'Libellé de mon adresse custom - 3 RUE DE VALOIS, 75008, Paris'
      )
    ).toBeVisible()
  })

  test('Create an offer with draft status and publish it', async ({
    authenticatedPage: page,
    checkAccessibility,
    offerDraft,
  }) => {
    await fillBasicOFferForm(page)
    await page.getByLabel('Autre adresse').click()
    await autoCompleteAddress(page)
    await fillOfferDetails(page, checkAccessibility)
    await fillDatesAndPrice(page, checkAccessibility)
    await fillInstitution(page, checkAccessibility)
    await expect(
      page.getByRole('heading', { name: 'Détails de l’offre' })
    ).toBeVisible()
    await page.getByText('Enregistrer et continuer').click()

    await Promise.all([
      page.waitForResponse(isGetCollectiveOffersBookableResponse),
      page.getByText('Sauvegarder le brouillon et quitter').click(),
    ])
    expect(page.getByText('Brouillon sauvegardé dans la liste des offres'))

    await page.getByRole('button', { name: 'Filtrer' }).click()
    await page.getByRole('button', { name: 'Statut' }).click()
    await page
      .getByTestId('panel-scrollable')
      .locator('label')
      .filter({ hasText: 'Brouillon' })
      .click()
    await page.getByRole('heading', { name: 'Offres réservables' }).click()
    await Promise.all([
      page.waitForResponse(isGetCollectiveOffersBookableResponse),
      page.getByText('Rechercher').click(),
    ])

    await expectCollectiveOffersAreFound(page, [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        commonOfferData.title,
        `${format(commonOfferData.date, 'dd/MM/yyyy')}`,
        `${commonOfferData.price}€${commonOfferData.participants} participants`,
        commonOfferData.institution,
        '3 RUE DE VALOIS 75008 Paris',
        'brouillon',
      ],
      [
        '',
        offerDraft.name,
        '-',
        '-',
        'DE LA TOUR',
        'À déterminer',
        'brouillon',
      ],
    ])

    await page.getByRole('link', { name: `${newOfferName}` }).click()
    await page.getByRole('link', { name: '5 Aperçu' }).click()
    await page.getByText('Publier l’offre').click()
    await page.getByText('Voir mes offres').click()
    await page.getByText('Réinitialiser les filtres').click()
    await searchOffer(page)

    await expectCollectiveOffersAreFound(page, [
      BOOKABLE_OFFERS_COLUMNS,
      [
        '',
        commonOfferData.title,
        `${format(commonOfferData.date, 'dd/MM/yyyy')}`,
        `${commonOfferData.price}€${commonOfferData.participants} participants`,
        commonOfferData.institution,
        '3 RUE DE VALOIS 75008 Paris',
        'publiée',
      ],
      [],
      [],
      [],
      [],
      [],
      [],
    ])
  })
})

async function fillBasicOFferForm(page: Page) {
  await Promise.all([
    page.waitForResponse(isGetDomainsResponse),
    page.getByText('Étape suivante').click(),
  ])

  await page.waitForResponse(isGetVenuesReponse)

  await page.getByLabel(/Structure/).selectOption(otherVenueName)
  await page.getByLabel(/Structure/).selectOption(otherVenueName)
  await expect(
    page.getByText('Mon Lieu 2 - 1 boulevard Poissonnière 75002 Paris')
  ).toBeVisible()

  await page.getByLabel(/Structure/).selectOption(venueName)
  await expect(
    page.getByText('Mon Lieu 1 - 1 boulevard Poissonnière 75002 Paris')
  ).toBeVisible()

  await page.getByLabel('Domaines artistiques').click()
  await page.getByLabel('Danse').click()
  await page.getByText('Quel est le type de votre offre ?').click()
  await page.getByLabel('Format').click()
  await page.getByLabel('Concert').click()
  await page.getByText('Quel est le type de votre offre ?').click()
}

async function fillOfferDetails(
  page: Page,
  checkAccessibility: (
    disabledRules?: string[]
  ) => Promise<AccessibilityResult>,
  withFormCheck = false
) {
  await page.getByLabel(/Titre de l’offre/).fill(commonOfferData.title)
  await page
    .getByLabel('Décrivez ici votre projet et son interêt pédagogique *')
    .fill(commonOfferData.description)
  await page.getByText('Collège').click()
  await page.getByText('6e').click()
  await page.getByLabel(/Email/).first().fill(commonOfferData.email)
  await page
    .getByLabel(/Email auquel envoyer les notifications/)
    .fill(commonOfferData.email)

  if (withFormCheck) {
    await page.getByLabel('Via un formulaire').click()
  }
  await checkAccessibility()

  await page.getByText('Enregistrer et continuer').click()
}

async function fillDatesAndPrice(
  page: Page,
  checkAccessibility: (disabledRules?: string[]) => Promise<AccessibilityResult>
) {
  await expect(
    page.getByRole('heading', {
      name: 'Indiquez le prix et la date de votre offre',
    })
  ).toBeVisible()
  await page
    .getByLabel(/Date de début */)
    .fill(format(commonOfferData.date, 'yyyy-MM-dd'))
  await page.getByLabel(/Horaire */).fill(commonOfferData.time)
  await page
    .getByLabel(/Nombre de participants */)
    .fill(commonOfferData.participants)
  await page.getByLabel(/Prix total TTC/).fill(commonOfferData.price)
  await page
    .getByLabel(/Informations sur le prix */)
    .fill(commonOfferData.priceDescription)
  await page
    .getByLabel(/Date limite de réservation */)
    .fill(format(commonOfferData.bookingLimitDate, 'yyyy-MM-dd'))
  await checkAccessibility()

  await Promise.all([
    page.waitForResponse(isPostCollectiveStocksResponse),
    page.getByText('Enregistrer et continuer').click(),
  ])
}

async function fillInstitution(
  page: Page,
  checkAccessibility: (disabledRules?: string[]) => Promise<AccessibilityResult>
) {
  await page
    .getByLabel(/Nom de l’établissement scolaire ou code UAI */)
    .fill(commonOfferData.institution)
  await Promise.all([
    page
      .locator('#list-institution')
      .getByText(new RegExp(commonOfferData.institution))
      .click(),
    page.waitForResponse(isGetInstitutionalRedactorsResponse),
  ])

  await checkAccessibility()
  await page.getByText('Enregistrer et continuer').click()
}

async function searchOffer(
  page: Page,
  waitForResponseFn: (response: Response) => boolean = (response: Response) =>
    isGetCollectiveOffersBookableResponse(response)
) {
  await page.getByRole('searchbox', { name: /Nom de l’offre/ }).clear()
  await page
    .getByRole('searchbox', { name: /Nom de l’offre/ })
    .fill(commonOfferData.title)

  await Promise.all([
    page.waitForResponse(waitForResponseFn),
    page.getByText('Rechercher').click(),
  ])
}

async function publishAndSearchOffer(
  page: Page,
  checkAccessibility: (
    disabledRules?: string[]
  ) => Promise<AccessibilityResult>,
  waitForResponseFn: (response: Response) => boolean = (response: Response) =>
    isGetCollectiveOffersBookableResponse(response)
) {
  await checkAccessibility()
  await page.getByText('Enregistrer et continuer').click()
  await expect(
    page.getByText(
      'Voici un aperçu de votre offre à destination de l’établissement scolaire sur la plateforme ADAGE.'
    )
  ).toBeVisible()
  await checkAccessibility()
  await page.getByText('Publier l’offre').click()

  await Promise.all([
    page.waitForResponse(waitForResponseFn),
    page.getByText('Voir mes offres').click(),
  ])

  await searchOffer(page, waitForResponseFn)
}
