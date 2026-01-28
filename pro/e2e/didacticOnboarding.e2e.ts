import type { Page } from '@playwright/test'

import { expect, test } from './fixtures/didacticOnboarding'

async function verifyDidacticOnboardingHomepage(page: Page): Promise<void> {
  await expect(page.getByTestId('spinner')).toHaveCount(0)
  await expect(
    page.getByText('Bienvenue sur le pass Culture Pro !')
  ).toBeVisible()
  await expect(
    page.getByText('Où souhaitez-vous diffuser votre première offre ?')
  ).toBeVisible()
  await expect(
    page.getByText('Sur l’application mobile à destination des jeunes')
  ).toBeVisible()
  await expect(
    page.getByText('Sur ADAGE à destination des enseignants')
  ).toBeVisible()
  await expect(page.getByText('Commencer')).toHaveCount(2)
}

async function fromOnboardingGoToCollectiveModal(page: Page): Promise<void> {
  await page.getByText('Aller au contenu').click()

  await page.getByLabel('Commencer la création d’offre sur ADAGE').click()
  await expect(
    page.getByRole('heading', { level: 1, name: 'Quelles sont les étapes ?' })
  ).toBeVisible()

  const depositLink = page.getByRole('link', { name: /Déposer un dossier/ })
  await expect(depositLink).toHaveAttribute('target', '_blank')
  await expect(depositLink).toHaveAttribute(
    'href',
    'https://demarche.numerique.gouv.fr/commencer/demande-de-referencement-sur-adage'
  )
}

async function fromOnboardingGoToFirstOfferCreation(page: Page): Promise<void> {
  await page.getByText('Aller au contenu').click()

  await page
    .getByLabel('Commencer la création d’offre sur l’application mobile')
    .click()
  await expect(
    page.getByRole('heading', {
      level: 1,
      name: 'Offre à destination des jeunes',
    })
  ).toBeVisible()
  await expect(
    page.getByRole('heading', {
      level: 2,
      name: 'Comment souhaitez-vous créer votre 1ère offre ?',
    })
  ).toBeVisible()
}

async function homePageLoaded(page: Page): Promise<void> {
  await expect(
    page.getByText('Bienvenue sur votre espace partenaire')
  ).toBeVisible()
  await expect(
    page.getByText(/Votre page partenaire|Vos pages partenaire/)
  ).toBeVisible()
  await expect(page.getByTestId('spinner')).toHaveCount(0)
}

test.describe('Didactic Onboarding feature', () => {
  test('I should not be able to onboard me by submitting an Adage referencing file if I don’t have an Adage ID', async ({
    authenticatedPage: page,
  }) => {
    await page.goto('/onboarding')
    await verifyDidacticOnboardingHomepage(page)

    await fromOnboardingGoToCollectiveModal(page)

    await page.getByRole('button', { name: /J’ai déposé un dossier/ }).click()

    await page.waitForResponse((response) =>
      response.url().includes('/eligibility')
    )

    await expect(
      page.getByText('Aucun dossier n’a été déposé par votre structure.')
    ).toBeVisible()
  })

  test('I should be able to onboard me by submitting an Adage referencing file if I have an Adage ID', async ({
    authenticatedPage: page,
  }) => {
    await page.goto('/onboarding')
    await verifyDidacticOnboardingHomepage(page)

    await fromOnboardingGoToCollectiveModal(page)

    await page.route('**/offerers/*/eligibility', async (route) => {
      const url = route.request().url()
      const offererIdMatch = url.match(/\/offerers\/(\d+)\//)
      const offererId = offererIdMatch![1]

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          offererId: Number(offererId),
          hasAdageId: true,
          hasDsApplication: null,
          isOnboarded: true,
        }),
      })
    })

    await page.getByRole('button', { name: /J’ai déposé un dossier/ }).click()

    await expect(page).toHaveURL(/\/accueil/)
    await homePageLoaded(page)
  })

  test('I should be able to create my first offer automatically', async ({
    authenticatedPage: page,
  }) => {
    await page.goto('/onboarding')
    await verifyDidacticOnboardingHomepage(page)

    await fromOnboardingGoToFirstOfferCreation(page)

    await page.getByRole('link', { name: 'Automatiquement' }).click()

    await expect(page).toHaveURL(/\/structures\/\d+\/lieux\/\d+\/parametres$/)
    await expect(
      page.getByRole('heading', { level: 1, name: 'Paramètres généraux' })
    ).toBeVisible()
    await expect(
      page.getByRole('heading', {
        level: 2,
        name: 'Gestion des synchronisations',
      })
    ).toBeVisible()
  })

  test('I should be able to start my first offer manually, saving and resume a draft offer, and publish it to get onboarded', async ({
    page,
  }) => {
    await page.goto('/onboarding')
    await verifyDidacticOnboardingHomepage(page)

    await fromOnboardingGoToFirstOfferCreation(page)

    const categoriesResponsePromise = page.waitForResponse((response) =>
      response.url().includes('/offers/categories')
    )
    await page.getByRole('link', { name: 'Manuellement' }).click()
    const categoriesResponse = await categoriesResponsePromise
    expect(categoriesResponse.ok()).toBeTruthy()

    await page
      .getByRole('textbox', { name: /Titre de l’offre/ })
      .fill('Mon offre en brouillon')

    const musicTypesResponsePromise = page.waitForResponse((response) =>
      response.url().includes('/offers/music-types')
    )
    await page
      .getByRole('combobox', { name: /Catégorie/ })
      .selectOption('Beaux-arts')
    await page.getByLabel(/Non accessible/).check()
    await musicTypesResponsePromise

    const postOfferResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/offers') &&
        response.request().method() === 'POST'
    )
    await page.getByRole('button', { name: 'Enregistrer et continuer' }).click()
    const postOfferResponse = await postOfferResponsePromise
    expect(postOfferResponse.ok()).toBeTruthy()

    const offersListResponsePromise = page.waitForResponse((response) =>
      response.url().includes('/offers?')
    )
    const categoriesResponse2Promise = page.waitForResponse((response) =>
      response.url().includes('/offers/categories')
    )
    await page.goto('/onboarding/individuel')
    await offersListResponsePromise
    await categoriesResponse2Promise

    await expect(
      page.getByRole('heading', {
        level: 2,
        name: 'Reprendre une offre déjà commencée',
      })
    ).toBeVisible()

    const getOfferResponsePromise = page.waitForResponse((response) =>
      /\/offers\/\d+$/.test(response.url())
    )
    await page.getByRole('link', { name: /Mon offre en brouillon/ }).click()
    const getOfferResponse = await getOfferResponsePromise
    expect(getOfferResponse.ok()).toBeTruthy()

    await expect(
      page.getByRole('heading', { level: 1, name: 'Créer une offre' })
    ).toBeVisible()
    await expect(
      page.getByRole('textbox', { name: /Titre de l’offre/ })
    ).toHaveValue('Mon offre en brouillon')

    const patchOfferResponsePromise = page.waitForResponse(
      (response) =>
        /\/offers\/\d+$/.test(response.url()) &&
        response.request().method() === 'PATCH'
    )
    await page.getByRole('button', { name: 'Enregistrer et continuer' }).click()
    await patchOfferResponsePromise

    // LOCALISATION STEP
    await expect(page).toHaveURL(/\/creation\/localisation/)
    const patchLocalisationResponsePromise = page.waitForResponse(
      (response) =>
        /\/offers\/\d+$/.test(response.url()) &&
        response.request().method() === 'PATCH'
    )
    await page.getByRole('button', { name: 'Enregistrer et continuer' }).click()
    await patchLocalisationResponsePromise

    // MEDIA STEP
    await expect(page).toHaveURL(/\/creation\/media/)
    const getStocksResponsePromise = page.waitForResponse(
      (response) =>
        /\/offers\/\d+\/stocks\/\?/.test(response.url()) &&
        response.request().method() === 'GET',
      { timeout: 60000 }
    )
    await page.getByText('Enregistrer et continuer').click()

    // PRICE CATEGORY STEP
    await expect(page).toHaveURL(/\/creation\/tarifs/)
    await getStocksResponsePromise

    await page.getByLabel(/Prix/).fill('42')

    const patchStocksResponsePromise = page.waitForResponse(
      (response) =>
        /\/offers\/\d+\/stocks\/$/.test(response.url()) &&
        response.request().method() === 'PATCH'
    )
    await page.getByRole('button', { name: 'Enregistrer et continuer' }).click()
    await patchStocksResponsePromise

    // USEFUL INFO STEP
    await expect(page).toHaveURL(/\/creation\/informations_pratiques/)
    const patchUsefulInfoResponsePromise = page.waitForResponse(
      (response) =>
        /\/offers\/\d+$/.test(response.url()) &&
        response.request().method() === 'PATCH'
    )
    await page.getByText('Enregistrer et continuer').click()
    await patchUsefulInfoResponsePromise

    // SUMMARY STEP
    await expect(
      page.getByRole('heading', { level: 2, name: 'Description' })
    ).toBeVisible()
    await expect(page.getByText('Vous y êtes presque !')).toBeVisible()

    const titleElements = page.getByText('Mon offre en brouillon')
    await expect(titleElements).toHaveCount(3)

    await expect(page.getByText('42,00 €')).toBeVisible()

    // PUBLISH OFFER STEP
    const publishOfferResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/offers/publish') &&
        response.request().method() === 'PATCH',
      { timeout: 120000 }
    )
    await page.getByRole('button', { name: 'Publier l’offre' }).click()
    await publishOfferResponsePromise

    await expect(
      page.getByRole('dialog', {
        name: 'Félicitations, vous avez créé votre offre !',
      })
    ).toBeVisible()

    await page.goto('/accueil')
    await homePageLoaded(page)
  })
})
