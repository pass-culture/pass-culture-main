import {
  expect,
  type Page,
  request as playwrightRequest,
  test,
} from '@playwright/test'
import { addDays, format } from 'date-fns'

import { MOCKED_BACK_ADDRESS_LABEL, mockAddressSearch } from './helpers/address'
import { expectCollectiveOffersAreFound } from './helpers/assertions'
import { login } from './helpers/auth'
import {
  BOOKABLE_OFFERS_COLUMNS,
  TEMPLATE_OFFERS_COLUMNS,
} from './helpers/constants'
import {
  BASE_API_URL,
  createProUserWithCollectiveOffers,
  type ProUserWithCollectiveOffersData,
} from './helpers/sandbox'

const newOfferName = 'Ma nouvelle offre collective créée'
const otherVenueName = 'Mon Lieu 2'
const venueName = 'Mon Lieu 1'
const venueFullAddress = '1 boulevard Poissonnière, 75002, Paris'
const defaultDate = addDays(new Date(), 2)
const defaultBookingLimitDate = addDays(new Date(), 1)

const commonOfferData = {
  title: newOfferName,
  description: 'Bookable draft offer',
  email: 'example@example.com',
  date: defaultDate,
  bookingLimitDate: defaultBookingLimitDate,
  time: '18:30',
  participants: '10',
  price: '10',
  priceDescription: 'description',
  institution: 'COLLEGE 123',
}

const SCHOOL_LOCATION_PATTERN = /Dans l.établissement/

async function createUserAndLogin(
  page: Page
): Promise<ProUserWithCollectiveOffersData> {
  const requestContext = await playwrightRequest.newContext({
    baseURL: BASE_API_URL,
  })

  const userData = await createProUserWithCollectiveOffers(requestContext)
  await requestContext.dispose()

  await login(page, userData.user.email)

  return userData
}

async function fillBasicOfferForm(page: Page) {
  const educationalDomainsResponsePromise = page.waitForResponse((response) =>
    response.url().includes('/collective/educational-domains')
  )
  await page.getByText('Étape suivante').click()
  await educationalDomainsResponsePromise
  await page.getByLabel(/Structure/).selectOption({ label: venueName })
  await expect(
    page.getByText('Mon Lieu 1 - 1 boulevard Poissonnière 75002 Paris')
  ).toBeVisible()
  await page.getByLabel(/Structure/).selectOption({ label: otherVenueName })
  await expect(
    page.getByText('Mon Lieu 2 - 1 boulevard Poissonnière 75002 Paris')
  ).toBeVisible()
  await page.getByLabel(/Structure/).selectOption({ label: venueName })
  await page.getByLabel('Domaines artistiques').click()
  await page.getByLabel('Danse').click()
  await page.getByText('Quel est le type de votre offre ?').click()
  await page.getByLabel('Formats').click()
  await page.getByLabel('Concert').click()
  await page.getByText('Quel est le type de votre offre ?').click()
}

async function fillOfferDetails(page: Page, data = commonOfferData) {
  await page.getByLabel(/Titre de l’offre/).fill(data.title)
  await page
    .getByLabel('Décrivez ici votre projet et son interêt pédagogique *')
    .fill(data.description)
  await page.getByText('Collège').click()
  await page.getByText('6e').click()
  await page.getByLabel(/Email/).first().fill(data.email)
  await page
    .getByLabel(/Email auquel envoyer les notifications/)
    .fill(data.email)
  await page.getByText('Enregistrer et continuer').click()
}

async function fillDatesAndPrice(page: Page, data = commonOfferData) {
  await page.getByLabel(/Date de début */).fill(format(data.date, 'yyyy-MM-dd'))
  await page.getByLabel(/Horaire */).fill(data.time)
  await page.getByLabel(/Nombre de participants */).fill(data.participants)
  await page.getByLabel(/Prix total TTC/).fill(data.price)
  await page
    .getByLabel(/Informations sur le prix */)
    .fill(data.priceDescription)
  await page
    .getByLabel(/Date limite de réservation */)
    .fill(format(data.bookingLimitDate, 'yyyy-MM-dd'))
  await page.getByText('Enregistrer et continuer').click()
}

async function fillInstitution(page: Page, data = commonOfferData) {
  await page
    .getByLabel(/Nom de l’établissement scolaire ou code UAI */)
    .fill(data.institution)
  const redactorsResponsePromise = page.waitForResponse((response) =>
    response.url().includes('/collective/offers/redactors')
  )
  await page
    .locator('#list-institution')
    .getByText(new RegExp(data.institution))
    .click()
  await redactorsResponsePromise
  await page.getByText('Enregistrer et continuer').click()
}

async function publishAndSearchOffer(page: Page, data = commonOfferData) {
  const bookableOffersAfterSearchPromise = page.waitForResponse((response) =>
    response.url().includes('/collective/bookable-offers')
  )

  page.getByRole('link', { name: 'Enregistrer et continuer' }).click()
  page.getByText('Publier l’offre').click()
  page.getByText('Voir mes offres').click()
  await bookableOffersAfterSearchPromise

  // Rechercher l'offre
  await page.getByRole('searchbox', { name: /Nom de l’offre/ }).clear()
  await page.getByRole('searchbox', { name: /Nom de l’offre/ }).fill(data.title)

  await page.getByText('Rechercher').click()
}

async function assertOfferInList(
  page: Page,
  title: string,
  location: string | RegExp,
  status = 'publiée',
  data = commonOfferData
) {
  const rows = page.locator('tbody').locator('tr[data-testid="table-row"]')
  await expect(rows.first()).toBeVisible({ timeout: 10000 })

  const row = rows.filter({ hasText: title })
  await expect(row.locator('td').nth(1)).toContainText(title)
  await expect(row.locator('td').nth(2)).toContainText(
    format(data.date, 'dd/MM/yyyy')
  )
  await expect(row.locator('td').nth(3)).toContainText(
    `${data.price}€${data.participants} participants`
  )
  await expect(row.locator('td').nth(4)).toContainText(data.institution)
  await expect(row.locator('td').nth(5)).toContainText(location)
  await expect(row.locator('td').nth(6)).toContainText(status)
}

test.describe('Create collective offers', () => {
  test('Create collective bookable offers with a precise address (the venue address, selected by default)', async ({
    page,
  }) => {
    await mockAddressSearch(page)
    await createUserAndLogin(page)

    await page.goto('/offre/creation')
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await fillBasicOfferForm(page)
    await fillOfferDetails(page)
    await expect(
      page.getByRole('heading', {
        name: 'Indiquez le prix et la date de votre offre',
      })
    ).toBeVisible()
    await fillDatesAndPrice(page)
    await fillInstitution(page)
    await expect(page.getByText(`Adresse : ${venueFullAddress}`)).toBeVisible()
    await publishAndSearchOffer(page)
    await assertOfferInList(
      page,
      `N°6${newOfferName}`,
      `${venueName} - 1 boulevard Poissonnière 75002 Paris`
    )
  })

  test('Create collective bookable offers with a precise address (another address)', async ({
    page,
  }) => {
    await mockAddressSearch(page)
    await createUserAndLogin(page)

    await page.goto('/offre/creation')
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await fillBasicOfferForm(page)
    await page.getByLabel('Autre adresse').click()
    await page.getByLabel(/Adresse postale/).fill(MOCKED_BACK_ADDRESS_LABEL)

    const responsePromise = page.waitForResponse((response) =>
      response.url().includes('data.geopf.fr/geocodage/search')
    )
    await responsePromise

    await page.getByTestId('list').getByText(MOCKED_BACK_ADDRESS_LABEL).click()
    await fillOfferDetails(page)
    await fillDatesAndPrice(page)
    await fillInstitution(page)
    await expect(
      page.getByText('Adresse : 3 RUE DE VALOIS, 75008, Paris')
    ).toBeVisible()
    await publishAndSearchOffer(page)
    await assertOfferInList(
      page,
      `N°6${newOfferName}`,
      '3 RUE DE VALOIS 75008 Paris'
    )
  })

  test('Create collective bookable offers with a precise address (another address - manual entry)', async ({
    page,
  }) => {
    await mockAddressSearch(page)
    await createUserAndLogin(page)

    await page.goto('/offre/creation')
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await fillBasicOfferForm(page)
    await page.getByLabel('Autre adresse').click()
    await page
      .getByLabel('Intitulé de la localisation')
      .fill('Libellé de mon adresse custom')
    await page.getByText('Vous ne trouvez pas votre adresse ?').click()
    await page
      .getByLabel(/Adresse postale/)
      .last()
      .fill('10 Rue du test')
    await page.getByLabel(/Code postal/).fill('75002')
    await page.getByLabel(/Ville/).fill('Paris')
    await page.getByLabel(/Coordonnées GPS/).fill('48.853320, 2.348979')
    await page.getByLabel(/Coordonnées GPS/).blur()
    await expect(
      page.getByText('Contrôlez la précision de vos coordonnées GPS.')
    ).toBeVisible()
    await fillOfferDetails(page)
    await fillDatesAndPrice(page)
    await fillInstitution(page)
    await expect(
      page.getByText('Intitulé : Libellé de mon adresse custom')
    ).toBeVisible()
    await expect(
      page.getByText('Adresse : 10 Rue du test, 75002, Paris')
    ).toBeVisible()
    await publishAndSearchOffer(page)
    await assertOfferInList(
      page,
      `N°6${newOfferName}`,
      '10 Rue du test 75002 Paris'
    )
  })

  test('Create collective bookable offers with school location', async ({
    page,
  }) => {
    await mockAddressSearch(page)
    await createUserAndLogin(page)

    await page.goto('/offre/creation')
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await fillBasicOfferForm(page)
    await page.getByLabel('En établissement scolaire').click()
    await fillOfferDetails(page)

    await fillDatesAndPrice(page)
    await fillInstitution(page)
    await expect(page.getByText(/Dans l.établissement scolaire/)).toBeVisible()
    await expect(
      page.getByText('Zone de mobilité : Paris (75) - Hauts-de-Seine (92)')
    ).toBeVisible()
    await publishAndSearchOffer(page)
    await assertOfferInList(page, `N°6${newOfferName}`, SCHOOL_LOCATION_PATTERN)
  })

  test('Create collective bookable offers with to be defined location', async ({
    page,
  }) => {
    await mockAddressSearch(page)
    await createUserAndLogin(page)

    await page.goto('/offre/creation')
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await fillBasicOfferForm(page)
    await page.getByLabel('À déterminer avec l’enseignant').click()
    await page.getByLabel('Commentaire').fill('Test commentaire')
    await fillOfferDetails(page)
    await fillDatesAndPrice(page)
    await fillInstitution(page)
    await expect(page.getByText('À déterminer avec l’enseignant')).toBeVisible()
    await expect(page.getByText('Commentaire : Test commentaire')).toBeVisible()
    await expect(
      page.getByText('Zone de mobilité : Paris (75) - Hauts-de-Seine (92)')
    ).toBeVisible()
    await publishAndSearchOffer(page)
    await assertOfferInList(page, `N°6${newOfferName}`, 'À déterminer')
  })

  test('Create collective offer template and use it in duplication page', async ({
    page,
  }) => {
    await mockAddressSearch(page)
    await createUserAndLogin(page)

    await page.goto('/offre/creation')
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await page.getByRole('radio', { name: /Une offre vitrine/ }).click()
    await page.getByText('Étape suivante').click()
    await fillBasicOfferForm(page)
    await page.getByLabel(/Titre de l’offre/).fill(commonOfferData.title)
    await page
      .getByLabel('Décrivez ici votre projet et son interêt pédagogique *')
      .fill(commonOfferData.description)
    await page.getByText('Collège').click()
    await page.getByText('6e').click()
    await page
      .getByLabel(/Email auquel envoyer les notifications/)
      .fill(commonOfferData.email)
    await page.getByLabel('Via un formulaire').click()
    await page.getByText('Enregistrer et continuer').click()
    await expect(page.getByText('Intitulé : Mon Lieu 1')).toBeVisible()
    await expect(page.getByText(`Adresse : ${venueFullAddress}`)).toBeVisible()
    await page.getByText('Enregistrer et continuer').click()
    await page.getByText('Publier l’offre').click()
    const offersTemplateAfterPublishPromise = page.waitForResponse((response) =>
      response.url().includes('/collective/offers-template')
    )
    await Promise.all([
      page.getByRole('button', { name: 'Voir mes offres' }).click(),
      offersTemplateAfterPublishPromise,
    ])

    // Rechercher l'offre
    await page.getByRole('searchbox', { name: /Nom de l’offre/ }).clear()
    await page
      .getByRole('searchbox', { name: /Nom de l’offre/ })
      .fill(commonOfferData.title)
    const offersTemplateAfterSearchPromise = page.waitForResponse((response) =>
      response.url().includes('/collective/offers-template')
    )
    await page.getByText('Rechercher').click()
    await offersTemplateAfterSearchPromise

    // Vérifier les résultats
    const templateResults = [
      TEMPLATE_OFFERS_COLUMNS,
      [
        '',
        `Offre vitrine${commonOfferData.title}`,
        'Toute l’année scolaire',
        `${venueName} - 1 boulevard Poissonnière 75002 Paris`,
        'publiée',
      ],
    ]
    await expectCollectiveOffersAreFound(page, templateResults)

    await page.goto('/offre/creation')
    await page
      .getByText('Dupliquer les informations d’une offre vitrine')
      .click()
    const offersTemplateForDuplicationPromise = page.waitForResponse(
      (response) => response.url().includes('/collective/offers-template')
    )
    await Promise.all([
      page.getByText('Étape suivante').click(),
      offersTemplateForDuplicationPromise,
    ])
    await page.getByText(newOfferName).click()
    await page.getByLabel(/Titre de l’offre/).clear()
    await page.getByLabel(/Titre de l’offre/).fill('Offre dupliquée OA')
    await page.getByLabel(/Email/).first().fill(commonOfferData.email)
    await page.getByText('Enregistrer et continuer').click()
    await fillDatesAndPrice(page)
    await fillInstitution(page)
    await expect(page.getByText('Intitulé : Mon Lieu 1')).toBeVisible()
    await expect(page.getByText(`Adresse : ${venueFullAddress}`)).toBeVisible()
    await publishAndSearchOffer(page, {
      ...commonOfferData,
      title: 'Offre dupliquée OA',
    })
    await assertOfferInList(
      page,
      'Offre dupliquée OA',
      `${venueName} - 1 boulevard Poissonnière 75002 Paris`
    )
  })

  test('Create collective bookable offers with a precise address (the venue address, selected by default) and update location', async ({
    page,
  }) => {
    await mockAddressSearch(page)
    await createUserAndLogin(page)

    await page.goto('/offre/creation')
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await fillBasicOfferForm(page)
    await fillOfferDetails(page)
    await fillDatesAndPrice(page)
    await fillInstitution(page)
    await expect(page.getByText(`Adresse : ${venueFullAddress}`)).toBeVisible()
    await publishAndSearchOffer(page)
    await assertOfferInList(
      page,
      `N°6${newOfferName}`,
      `${venueName} - 1 boulevard Poissonnière 75002 Paris`
    )

    await page.getByRole('link', { name: `N°6 ${newOfferName}` }).click()
    await page.getByText('Modifier').first().click()
    await page.getByLabel('Autre adresse').click()
    await page.getByLabel('Intitulé de la localisation').clear()
    await page
      .getByLabel('Intitulé de la localisation')
      .fill('Libellé de mon adresse custom')
    await page.getByLabel(/Adresse postale/).fill(MOCKED_BACK_ADDRESS_LABEL)

    const responsePromise = page.waitForResponse((response) =>
      response.url().includes('data.geopf.fr/geocodage/search')
    )
    await responsePromise

    await page.getByTestId('list').getByText(MOCKED_BACK_ADDRESS_LABEL).click()
    await page.getByText('Enregistrer et continuer').click()
    await expect(page.getByText('Libellé de mon adresse custom')).toBeVisible()
    await expect(page.getByText('3 RUE DE VALOIS, 75008, Paris')).toBeVisible()
  })

  test('Create an offer with draft status and publish it', async ({ page }) => {
    await mockAddressSearch(page)
    const userData = await createUserAndLogin(page)

    await page.goto('/offre/creation')
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await fillBasicOfferForm(page)
    await page.getByLabel('Autre adresse').click()
    await page.getByLabel(/Adresse postale/).fill(MOCKED_BACK_ADDRESS_LABEL)

    const responsePromise = page.waitForResponse((response) =>
      response.url().includes('data.geopf.fr/geocodage/search')
    )
    await responsePromise

    await page.getByTestId('list').getByText(MOCKED_BACK_ADDRESS_LABEL).click()
    await fillOfferDetails(page)
    await fillDatesAndPrice(page)
    await fillInstitution(page)

    await expect(
      page.getByRole('heading', { name: 'Détails de l’offre' })
    ).toBeVisible()
    await page.getByText('Enregistrer et continuer').click()

    const bookableOffersAfterSavePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/bookable-offers') &&
        response.status() === 200
    )
    await page.getByText('Sauvegarder le brouillon et quitter').click()

    await expect(
      page.getByText('Brouillon sauvegardé dans la liste des offres')
    ).toBeVisible()

    await bookableOffersAfterSavePromise

    await page.getByText('Filtrer').click()

    await page.getByRole('button', { name: 'Statut' }).click()
    const panelScrollable = page.getByTestId('panel-scrollable')
    await panelScrollable.evaluate((el) => {
      el.scrollTop = el.scrollHeight
    })
    await panelScrollable.getByText('Brouillon').click()

    await page.getByRole('heading', { name: 'Offres réservables' }).click()
    const bookableOffersAfterDraftFilterPromise = page.waitForResponse(
      (response) => response.url().includes('/collective/bookable-offers')
    )
    await page.getByText('Rechercher').click()
    await bookableOffersAfterDraftFilterPromise

    const draftResults = [
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
        userData.offerDraft.name,
        '-',
        '-',
        'DE LA TOUR',
        'À déterminer',
        'brouillon',
      ],
    ]

    await expectCollectiveOffersAreFound(page, draftResults)

    const educationalPromise = page.waitForResponse(
      (response) =>
        response.url().includes('/offerers/educational') &&
        response.request().method() === 'GET'
    )
    await page.getByRole('link', { name: `N°6 ${newOfferName}` }).click()
    await educationalPromise

    await expect(page.getByRole('link', { name: '5 Aperçu' })).toBeVisible({
      timeout: 10000,
    })
    await page.getByRole('link', { name: '5 Aperçu' }).click()

    await expect(
      page.getByRole('button', { name: 'Publier l’offre' })
    ).toBeVisible({ timeout: 10000 })
    await page.getByText('Publier l’offre').click()
    await page.getByText('Voir mes offres').click()

    await expect(page).toHaveURL(/\/offres\/collectives/)

    await page.getByText('Réinitialiser les filtres').click()
    await page
      .getByRole('searchbox', { name: /Nom de l’offre/ })
      .fill(newOfferName)
    const bookableOffersAfterResetPromise = page.waitForResponse((response) =>
      response.url().includes('/collective/bookable-offers')
    )
    await page.getByText('Rechercher').click()
    await bookableOffersAfterResetPromise
    await assertOfferInList(
      page,
      `N°6${newOfferName}`,
      '3 RUE DE VALOIS 75008 Paris'
    )
  })
})
