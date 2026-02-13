import * as path from 'node:path'
import type { Page, TestInfo } from '@playwright/test'

import type { AccessibilityResult } from './fixtures/common'
import { expect, test } from './fixtures/createIndividualOffer'
import {
  autoCompleteAddress,
  fillCustomAddress,
  mockAddressSearch,
} from './helpers/address'
import { expectIndividualOffersOrBookingsAreFound } from './helpers/assertions'
import {
  isGetCategoriesResponse,
  isGetOfferResponse,
  isGetOffersResponse,
  isPatchOffersResponse,
  isPostEventStocksResponse,
  isPostOfferResponse,
  isPublishOfferResponse,
  isPutPriceCategoriesResponse,
} from './helpers/requests'

async function handleImageUpload(
  page: Page,
  testInfo: TestInfo,
  checkAccessibility: (disabledRules?: string[]) => Promise<AccessibilityResult>
) {
  await page
    .getByLabel('Importez une image')
    .setInputFiles(
      path.join(testInfo.project.testDir, 'common/data/librairie.jpeg')
    )

  await expect(page.getByTestId('spinner').first()).not.toBeVisible()

  await page
    .getByLabel('Crédit de l’image')
    .fill('Les êtres les plus intelligents de l’univers')

  await page.getByTestId('slider').fill('1.7')
  await page.getByText('Importer').click()
  await expect(page.getByTestId('image-preview')).toBeVisible()
  await expect(page.getByTestId('image-preview')).toHaveJSProperty(
    'naturalWidth',
    470
  )
  await expect(page.getByTestId('image-preview')).toHaveJSProperty(
    'naturalHeight',
    705
  )

  await checkAccessibility()
  await page.getByText('Enregistrer et continuer').click()
}

test.describe('Create individual offers new flow', () => {
  test.beforeEach(async ({ authenticatedPage: page }) => {
    await page.goto('/offre/individuelle/creation/description')
  })

  test('I should be able to create an individual show offer', async ({
    authenticatedPage: page,
    checkAccessibility,
  }, testInfo) => {
    await mockAddressSearch(page)

    await page.getByLabel(/Titre de l’offre/).fill('Le Diner de Devs')
    await page
      .getByLabel(/Description/)
      .fill('Une PO invite des développeurs à dîner...')
    await page.getByLabel('Catégorie').selectOption('Spectacle vivant')
    await page
      .getByLabel(/Sous-catégorie/)
      .selectOption('Spectacle, représentation')
    await page.getByLabel(/Type de spectacle/).selectOption('Théâtre')
    await page.getByLabel(/Sous-type/).selectOption('Comédie')
    await page.getByLabel(/Non accessible/).check()

    await checkAccessibility()
    await page.getByText('Enregistrer et continuer').click()

    await expect(
      page.getByRole('heading', { name: 'Où profiter de l’offre ?' })
    ).toBeVisible()
    await page.getByLabel('À une autre adresse').click()
    await page
      .getByLabel('Intitulé de la localisation')
      .fill('Libellé de mon adresse')

    await autoCompleteAddress(page)

    await Promise.all([
      page.waitForResponse(isPatchOffersResponse),
      page.getByText('Enregistrer et continuer').click(),
    ])

    await handleImageUpload(page, testInfo, checkAccessibility)
    await expect(page.getByLabel('Intitulé du tarif')).toHaveValue(
      'Tarif unique'
    )
    await page.getByText('Ajouter un tarif').click()
    await page.getByText('Ajouter un tarif').click()
    await page.getByText('Ajouter un tarif').click()

    const titles = await page.getByText('Intitulé du tarif').all()
    const prices = await page.getByText(/Prix/).all()
    const freeCheckbox = await page
      .getByRole('checkbox', { name: /Gratuit/ })
      .all()

    await titles[0].clear()
    await titles[0].fill('Carré Or')
    await prices[0].fill('100')

    await titles[1].fill('Fosse Debout')
    await prices[1].fill('10')

    await titles[2].fill('Fosse Sceptique')
    await freeCheckbox[2].check()

    await titles[3].fill('Prix à supprimer')
    await prices[3].fill('40')

    await expect(
      page.getByText('Accepter les réservations “Duo“')
    ).toBeVisible()

    checkAccessibility()
    await Promise.all([
      page.waitForResponse(isPutPriceCategoriesResponse),
      page.getByText('Enregistrer et continuer').click(),
    ])

    await expect(page.getByText('Définir le calendrier')).toBeVisible()
    await page.getByRole('button', { name: 'Retour' }).click()

    await expect(page.getByLabel('Intitulé du tarif')).toHaveCount(4)

    await page
      .getByRole('button', { name: /Supprimer ce tarif/ })
      .last()
      .click()
    await expect(page.getByLabel('Intitulé du tarif')).toHaveCount(3)

    await Promise.all([
      page.waitForResponse(isPutPriceCategoriesResponse),
      page.getByText('Enregistrer et continuer').click(),
    ])

    await page.getByRole('button', { name: 'Définir le calendrier' }).click()
    await page.getByLabel('Toutes les semaines').click()
    await page.getByLabel('Vendredi').click()
    await page.getByLabel('Samedi').click()
    await page.getByLabel('Dimanche').click()
    await page.getByLabel(/Du/).fill('2030-05-01')
    await page.getByLabel(/Au/).fill('2030-09-30')
    await page.getByLabel(/Horaire 1/).fill('18:30')
    await page.getByText('Ajouter un créneau').click()
    await page.getByLabel(/Horaire 2/).fill('21:00')

    await page.getByText('Ajouter d’autres places et tarifs').click()
    expect(
      await page.getByTestId(/wrapper-quantityPerPriceCategories/).count()
    ).toEqual(2)

    const row = await page
      .getByTestId(/wrapper-quantityPerPriceCategories/)
      .all()

    await row[0].getByLabel(/Tarif/).selectOption('0,00\xa0€ - Fosse Sceptique')
    await row[0].getByLabel('Nombre de places').fill('100')

    await row[1].getByLabel(/Tarif/).selectOption('10,00\xa0€ - Fosse Debout')
    await row[1].getByLabel('Nombre de places').fill('20')

    await page.getByText('Ajouter d’autres places et tarifs').click()
    expect(
      await page.getByTestId(/wrapper-quantityPerPriceCategories/).count()
    ).toEqual(3)

    await page
      .getByTestId(/wrapper-quantityPerPriceCategories/)
      .last()
      .getByLabel(/Tarif/)
      .selectOption('100,00\xa0€ - Carré Or')

    await page
      .getByLabel('Nombre de jours avant le début de l’évènement')
      .fill('3')

    checkAccessibility()
    await Promise.all([
      page.waitForResponse(isPostEventStocksResponse),
      page.getByText('Valider').click(),
    ])

    checkAccessibility()
    await page.getByText('Enregistrer et continuer').click()

    await page.getByLabel('Retrait sur place (guichet, comptoir...)').click()
    await page
      .getByLabel(/Email de contact communiqué aux bénéficiaires/)
      .fill('passculture@example.com')

    checkAccessibility()
    await page.getByText('Enregistrer et continuer').click()

    await expect(
      page.getByRole('heading', { name: 'Publication et réservation' })
    ).toBeVisible()

    checkAccessibility()
    await Promise.all([
      page.waitForResponse(isGetOfferResponse),
      page.waitForResponse(isPublishOfferResponse),
      page.getByText('Publier l’offre').click(),
    ])

    await page.getByRole('button', { name: 'Plus tard' }).click()
    await Promise.all([
      page.waitForResponse(isGetOffersResponse),
      page.waitForResponse(isGetCategoriesResponse),
      page.getByText('Voir la liste des offres').click(),
    ])

    expect(page.url().includes('/offers'))
    await expect(
      page.getByRole('cell', { name: 'Le Diner de Devs' }).first()
    ).toBeVisible()
    await expect(
      page.getByRole('cell', {
        name: 'Libellé de mon adresse - 3 RUE DE VALOIS 75008 Paris',
      })
    ).toBeVisible()
    await expect(await page.getByText('396 dates')).toBeVisible()
  })

  test('I should be able to create a physical book individual offer', async ({
    authenticatedPage: page,
    checkAccessibility,
  }, testInfo) => {
    await mockAddressSearch(page)

    const offerTitle = 'H2G2 Le Guide du voyageur galactique'
    const offerDesc =
      'Une quête pour obtenir la question ultime sur la vie, l’univers et tout le reste.'

    await page.getByLabel(/Titre de l’offre/).fill(offerTitle)
    await page.getByLabel(/Description/).fill(offerDesc)
    const ean = String(
      Math.floor(1000000000000 + Math.random() * 9000000000000)
    )
    await page.getByLabel(/Catégorie/).selectOption('Livre')
    await page.getByLabel(/Sous-catégorie/).selectOption('Livre papier')
    await page.getByLabel(/Non accessible/).check()
    await page.getByLabel(/Auteur/).fill('Douglas Adams')
    await page.getByLabel('EAN-13 (European Article Numbering)').fill(ean)
    await expect(page.getByLabel(/Titre de l’offre/)).toHaveValue(offerTitle)
    await expect(page.getByLabel(/Description/)).toHaveText(offerDesc)

    await Promise.all([
      page.waitForResponse(isPostOfferResponse),
      page.getByText('Enregistrer et continuer').click(),
    ])

    await expect(
      page.getByRole('heading', { name: 'Où profiter de l’offre ?' })
    ).toBeVisible()
    await page.getByLabel('À une autre adresse').click()
    await fillCustomAddress(page, expect)
    await Promise.all([
      page.waitForResponse(isPatchOffersResponse),
      page.getByText('Enregistrer et continuer').click(),
    ])

    await handleImageUpload(page, testInfo, checkAccessibility)

    await page.getByLabel(/Prix/).fill('42')
    await page.getByLabel('Date limite de réservation').fill('2042-05-03')
    await page.getByLabel(/Stock/).fill('42')
    checkAccessibility()
    await Promise.all([
      page.waitForResponse(isPatchOffersResponse),
      page.getByText('Enregistrer et continuer').click(),
    ])

    await page
      .getByLabel('Informations complémentaires')
      .fill('Seuls les dauphins et les souris peuvent le lire.')
    await page.getByLabel('Être notifié par email des réservations').click()

    await page.getByText('Enregistrer et continuer').click()

    await Promise.all([
      page.waitForResponse(isGetOfferResponse),
      page.waitForResponse(isPublishOfferResponse),
      page.getByText('Publier l’offre').click(),
    ])

    await page.getByText('Voir la liste des offres').click()
    const expectedNewResults = [
      ['', "Nom de l'offre", 'Lieu', 'Stocks', 'Statut', ''],
      [
        '',
        offerTitle,
        'Libellé de mon adresse custom - Place de la gare 12312 Y',
        '42',
        'publiée',
      ],
      [],
    ]
    await expectIndividualOffersOrBookingsAreFound(page, expectedNewResults)
    await expect(page.getByText(ean)).toBeVisible()
  })
})
