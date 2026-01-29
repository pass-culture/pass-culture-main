import * as path from 'node:path'
import {
  expect,
  type Page,
  request as playwrightRequest,
  test,
} from '@playwright/test'

import { logAccessibilityViolations } from './helpers/accessibility'
import { MOCKED_BACK_ADDRESS_LABEL, mockAddressSearch } from './helpers/address'
import { expectIndividualOffersOrBookingsAreFound } from './helpers/assertions'
import { login } from './helpers/auth'
import { BASE_API_URL, createRegularProUser } from './helpers/sandbox'

async function setSliderValue(page: Page, value: number) {
  const slider = page.locator('input[type=range]')
  await slider.evaluate((el: HTMLInputElement, val: number) => {
    el.value = String(val)
    el.dispatchEvent(new Event('input', { bubbles: true }))
  }, value)
}

test.describe('Create individual offers new flow', () => {
  test('I should be able to create an individual show offer', async ({
    page,
  }) => {
    await mockAddressSearch(page)

    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const userData = await createRegularProUser(requestContext)
    await requestContext.dispose()
    await login(page, userData.user.email)

    await page.goto('/offre/individuelle/creation/description')
    await expect(page.getByTestId('spinner')).not.toBeVisible()

    // DESCRIPTION STEP
    await page.getByLabel(/Titre de l’offre/).fill('Le Diner de Devs')

    await page
      .getByLabel('Description')
      .fill('Une PO invite des développeurs à dîner...')
    await page.getByLabel(/Catégorie/).selectOption('Spectacle vivant')
    await page
      .getByLabel(/Sous-catégorie/)
      .selectOption('Spectacle, représentation')
    await page.getByLabel(/Type de spectacle/).selectOption('Théâtre')
    await page.getByLabel(/Sous-type/).selectOption('Comédie')

    await page.getByLabel(/Non accessible/).check()

    await logAccessibilityViolations(page)

    const postOfferPromise = page.waitForResponse(
      (r) => r.url().includes('/offers') && r.request().method() === 'POST'
    )

    await page.getByText('Enregistrer et continuer').click()

    await postOfferPromise

    // LOCATION STEP
    await expect(
      page.getByRole('heading', { name: 'Où profiter de l’offre ?' })
    ).toBeVisible()

    await page.getByLabel('À une autre adresse').click()
    await page
      .getByLabel('Intitulé de la localisation')
      .fill('Libellé de mon adresse')
    await page.getByLabel(/Adresse postale/).fill(MOCKED_BACK_ADDRESS_LABEL)

    await page.waitForResponse((r) =>
      r.url().includes('data.geopf.fr/geocodage/search')
    )

    await page.getByTestId('list').getByText(MOCKED_BACK_ADDRESS_LABEL).click()

    const patchOfferLocationPromise = page.waitForResponse(
      (r) => r.url().includes('/offers/') && r.request().method() === 'PATCH'
    )

    await page.getByText('Enregistrer et continuer').click()

    await patchOfferLocationPromise

    // MEDIA STEP
    const imageFilePath = path.join(process.cwd(), 'e2e/assets/librairie.jpeg')
    await page.getByLabel('Importez une image').setInputFiles(imageFilePath)
    await expect(page.getByTestId('spinner')).not.toBeVisible()
    await page
      .getByLabel('Crédit de l’image')
      .fill('Les êtres les plus intelligents de l’univers')
    await setSliderValue(page, 1.7)
    await page.getByText('Importer').click()

    const imagePreview = page.getByTestId('image-preview')
    await expect(imagePreview).toBeVisible()
    const naturalWidth = await imagePreview.evaluate(
      (img: HTMLImageElement) => img.naturalWidth
    )
    const naturalHeight = await imagePreview.evaluate(
      (img: HTMLImageElement) => img.naturalHeight
    )
    expect(naturalWidth).toBe(800)
    expect(naturalHeight).toBe(1200)

    await logAccessibilityViolations(page)

    await page.getByText('Enregistrer et continuer').click()

    // PRICE CATEGORIES STEP
    await expect(page.getByLabel('Intitulé du tarif').first()).toHaveValue(
      'Tarif unique'
    )
    await page.getByText('Ajouter un tarif').click()
    await page.getByText('Ajouter un tarif').click()
    await page.getByText('Ajouter un tarif').click()

    await page.getByLabel('Intitulé du tarif').nth(0).clear()
    await page.getByLabel('Intitulé du tarif').nth(0).fill('Carré Or')
    await page.getByLabel(/Prix/).nth(0).fill('100')

    await page.getByLabel('Intitulé du tarif').nth(1).fill('Fosse Debout')
    await page.getByLabel(/Prix/).nth(1).fill('10')

    await page.getByLabel('Intitulé du tarif').nth(2).fill('Fosse Sceptique')
    await page.getByRole('checkbox', { name: 'Gratuit' }).nth(2).click()
    // add a price category to delete it later
    await page.getByLabel('Intitulé du tarif').nth(3).fill('Prix à supprimer')
    await page.getByLabel(/Prix/).nth(3).fill('40')

    await expect(
      page.getByText(/Accepter les réservations .Duo./)
    ).toBeVisible()
    await logAccessibilityViolations(page)

    const priceCategoriesPromise1 = page.waitForResponse(
      (r) =>
        r.url().includes('/offers/') && r.url().includes('/price_categories')
    )
    await page.getByText('Enregistrer et continuer').click()
    await priceCategoriesPromise1

    await expect(page.getByText('Définir le calendrier').first()).toBeVisible()
    // we go back to price categories step to delete a price category
    await page.getByText('Retour').click()
    // we click on delete button of the last price category
    await page.getByTestId('remove-price-table-entry-button-3').click()
    await expect(page.getByLabel('Intitulé du tarif')).toHaveCount(3)

    const priceCategoriesPromise2 = page.waitForResponse(
      (r) =>
        r.url().includes('/offers/') && r.url().includes('/price_categories')
    )

    await page.getByText('Enregistrer et continuer').click()

    // we assert that only 3 priceCategories are present in the response
    const priceCategoriesResponse = await priceCategoriesPromise2
    const priceCategoriesBody = await priceCategoriesResponse.json()
    expect(priceCategoriesBody.priceCategories).toHaveLength(3)

    // RECURRENCE FORM DIALOG
    await page.getByRole('button', { name: 'Définir le calendrier' }).click()

    await page.getByText('Toutes les semaines').click()
    await page.getByLabel('Vendredi').click()
    await page.getByLabel('Samedi').click()
    await page.getByLabel('Dimanche').click()
    await page.getByLabel('Du *').fill('2030-05-01')
    await page.getByLabel('Au *').fill('2030-09-30')
    await page.getByLabel(/Horaire 1/).fill('18:30')
    await page.getByText('Ajouter un créneau').click()
    await page.getByLabel(/Horaire 2/).fill('21:00')
    await page.getByText('Ajouter d’autres places et tarifs').click()

    await page
      .getByTestId('wrapper-quantityPerPriceCategories.0')
      .getByLabel(/Tarif/)
      .selectOption('0,00\u00a0€ - Fosse Sceptique')

    await page.getByLabel('Nombre de places').nth(0).fill('100')

    await page.getByText('Ajouter d’autres places et tarifs').click()

    await page
      .getByTestId('wrapper-quantityPerPriceCategories.1')
      .getByLabel(/Tarif/)
      .selectOption('10,00\u00a0€ - Fosse Debout')

    await page.getByLabel('Nombre de places').nth(1).fill('20')

    await expect(
      page.getByTestId('wrapper-quantityPerPriceCategories.2')
    ).toBeVisible()
    await page
      .getByTestId('wrapper-quantityPerPriceCategories.2')
      .getByLabel(/Tarif/)
      .selectOption('100,00\u00a0€ - Carré Or')

    await page
      .getByLabel('Nombre de jours avant le début de l’évènement')
      .fill('3')

    await logAccessibilityViolations(page)

    const postStocksPromise = page.waitForResponse(
      (r) => r.url().includes('/stocks/bulk') && r.request().method() === 'POST'
    )

    await page.getByText('Valider').click()

    await postStocksPromise

    await logAccessibilityViolations(page)
    await page.getByText('Enregistrer et continuer').click()

    // USEFUL INFORMATIONS STEP
    await page.getByText('Retrait sur place (guichet, comptoir...)').click()
    await page
      .getByLabel(/Email de contact communiqué aux bénéficiaires/)
      .fill('passculture@example.com')

    await logAccessibilityViolations(page)

    await page.getByText('Enregistrer et continuer').click()

    // SUMMARY STEP
    await logAccessibilityViolations(page)

    await page.getByText('Publier l’offre').click()

    // CONFIRMATION STEP
    const publishOfferPromise = page.waitForResponse(
      (r) =>
        r.url().includes('/offers/publish') && r.request().method() === 'PATCH'
    )
    const getOfferAfterPublishPromise = page.waitForResponse(
      (r) => r.url().includes('/offers/') && r.request().method() === 'GET'
    )

    await page
      .getByRole('dialog', { name: /Félicitations/ })
      .getByRole('button', { name: 'Plus tard' })
      .click()

    await Promise.all([publishOfferPromise, getOfferAfterPublishPromise])

    // OFFERS LIST
    const getOffersListPromise = page.waitForResponse((r) =>
      r.url().includes('/offers?')
    )
    const getCategoriesPromise3 = page.waitForResponse((r) =>
      r.url().includes('/offers/categories')
    )

    await page.getByRole('link', { name: 'Voir la liste des offres' }).click()

    await Promise.all([getOffersListPromise, getCategoriesPromise3])

    await expect(page).toHaveURL(/\/offres/)
    await expect(
      page.getByRole('row', { name: /Le Diner de Devs/ })
    ).toBeVisible()
    await expect(
      page.getByRole('row', {
        name: /Libellé de mon adresse - 3 RUE DE VALOIS 75008 Paris/,
      })
    ).toBeVisible()
    await expect(page.getByRole('row', { name: /396 dates/ })).toBeVisible()
  })

  test('I should be able to create a physical book individual offer', async ({
    page,
  }) => {
    await mockAddressSearch(page)

    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const userData = await createRegularProUser(requestContext)
    await requestContext.dispose()
    await login(page, userData.user.email)

    const offerTitle = 'H2G2 Le Guide du voyageur galactique'
    const offerDesc =
      'Une quête pour obtenir la question ultime sur la vie, l’univers et tout le reste.'

    await page.goto('/offre/individuelle/creation/description')
    await expect(page.getByTestId('spinner')).not.toBeVisible()

    // DESCRIPTION STEP
    await page.getByLabel(/Titre de l’offre/).fill(offerTitle)
    await page.getByLabel('Description').fill(offerDesc)

    // Random 13-digit number because we can't use the same EAN twice
    const ean = String(
      Math.floor(1000000000000 + Math.random() * 9000000000000)
    )

    await page.getByLabel(/Catégorie/).selectOption('Livre')
    await page.getByLabel(/Sous-catégorie/).selectOption('Livre papier')
    await page.getByLabel(/Non accessible/).check()
    await page.getByLabel('Auteur').fill('Douglas Adams')
    await page.getByLabel('EAN-13 (European Article Numbering)').fill(ean)

    await expect(page.getByLabel(/Titre de l’offre/)).toHaveValue(offerTitle)
    await expect(page.getByLabel('Description')).toHaveText(offerDesc)

    const postOfferPromise = page.waitForResponse(
      (r) => r.url().includes('/offers') && r.request().method() === 'POST'
    )

    await page.getByText('Enregistrer et continuer').click()

    await postOfferPromise

    // LOCATION STEP
    await expect(
      page.getByRole('heading', { name: 'Où profiter de l’offre ?' })
    ).toBeVisible()
    await page.getByLabel('À une autre adresse').click()
    await page.getByText('Vous ne trouvez pas votre adresse ?').click()
    await page
      .getByLabel('Intitulé de la localisation')
      .fill('Libellé de mon adresse custom')
    await page
      .getByLabel(/Adresse postale/)
      .last()
      .fill('Place de la gare')
    await page.getByLabel(/Code postal/).fill('123123')
    await page.getByLabel(/Ville/).fill('Y')
    await page.getByLabel(/Coordonnées GPS/).fill('48.853320, 2.348979')
    await page.getByLabel(/Coordonnées GPS/).blur()
    await expect(
      page.getByText('Contrôlez la précision de vos coordonnées GPS.')
    ).toBeVisible()

    const patchOfferLocationPromise = page.waitForResponse(
      (r) => r.url().includes('/offers/') && r.request().method() === 'PATCH'
    )

    await page.getByText('Enregistrer et continuer').click()

    await patchOfferLocationPromise

    // MEDIA STEP
    const imageFilePath = path.join(process.cwd(), 'e2e/assets/librairie.jpeg')
    await page.getByLabel('Importez une image').setInputFiles(imageFilePath)
    await expect(page.getByTestId('spinner')).not.toBeVisible()
    await page
      .getByLabel('Crédit de l’image')
      .fill('Les êtres les plus intelligents de l’univers')
    await setSliderValue(page, 1.7)
    await page.getByText('Importer').click()
    await page.getByText('Enregistrer et continuer').click()

    await expect(page).toHaveURL(/\/creation\/media/)

    const getStocksPromise = page.waitForResponse(
      (r) => r.url().includes('/offers/') && r.url().includes('/stocks/')
    )

    await page.getByText('Enregistrer et continuer').click()

    await getStocksPromise

    // STOCKS STEP
    await page.getByLabel(/Prix/).fill('42')
    await page.getByLabel('Date limite de réservation').fill('2042-05-03')
    await page.getByLabel(/Stock/).fill('42')

    const patchStocksPromise = page.waitForResponse(
      (r) =>
        r.url().includes('/offers/') &&
        r.url().includes('/stocks') &&
        r.request().method() === 'PATCH'
    )

    await page.getByText('Enregistrer et continuer').click()

    await patchStocksPromise

    // USEFUL INFORMATIONS STEP
    await page
      .getByLabel('Informations complémentaires')
      .fill('Seuls les dauphins et les souris peuvent le lire.')
    await page.getByText('Être notifié par email des réservations').click()
    await page.getByText('Enregistrer et continuer').click()

    // SUMMARY STEP
    const publishOfferPromise = page.waitForResponse(
      (r) =>
        r.url().includes('/offers/publish') && r.request().method() === 'PATCH'
    )
    const getOfferAfterPublishPromise = page.waitForResponse(
      (r) => r.url().includes('/offers/') && r.request().method() === 'GET'
    )

    await page.getByText('Publier l’offre').click()

    await Promise.all([publishOfferPromise, getOfferAfterPublishPromise])

    await page
      .getByRole('dialog', { name: /Félicitations/ })
      .getByRole('button', { name: 'Plus tard' })
      .click()

    const getOffersListPromise = page.waitForResponse((r) =>
      r.url().includes('/offers?')
    )

    await page.getByRole('link', { name: 'Voir la liste des offres' }).click()
    await expect(page).toHaveURL(/\/offres/)
    await getOffersListPromise

    // OFFERS LIST
    const expectedNewResults = [
      ['', 'Nom de l’offre', 'Lieu', 'Stocks', 'Statut', ''],
      [
        '',
        offerTitle,
        'Libellé de mon adresse custom - Place de la gare 12312 Y',
        '42',
        'publiée',
      ],
    ]

    await expectIndividualOffersOrBookingsAreFound(page, expectedNewResults)
    await expect(page.getByText(ean)).toBeVisible()
  })
})
