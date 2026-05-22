import { expect, test } from './fixtures/didacticOnboarding'
import {
  isGetCategoriesResponse,
  isGetOfferResponse,
  isGetOffersResponse,
  isPatchOffersResponse,
  isPatchStocksResponse,
  isPublishOfferResponse,
  isSynchronizeOffererOnboardingResponse,
} from './helpers/requests'

test.describe('Didactic Onboarding feature', () => {
  test.beforeEach(async ({ authenticatedPage: page }) => {
    await page.goto('/accueil')
    await expect(
      page.getByText('Bienvenue sur pass Culture Pro !')
    ).toBeVisible()
    await expect(
      page.getByText(
        /Notre équipe vous contactera par email pour vous demander vos justificatifs d’inscription./
      )
    ).toBeVisible()
    await expect(page.getByText(/Pensez à vérifier vos spams./)).toBeVisible()
    await expect(
      page.getByText('Où souhaitez-vous diffuser votre première offre ?')
    ).toBeVisible()
    await expect(
      page.getByText('Sur l’application mobile à destination des jeunes')
    ).toBeVisible()
    await expect(
      page.getByText('Sur ADAGE à destination des enseignants')
    ).toBeVisible()
  })

  test('I should be able to skip the onboarding', async ({
    authenticatedPage: page,
  }) => {
    // Should not be able to go to home page
    await page.goto('/accueil')
    await expect(
      page.getByText('Où souhaitez-vous diffuser votre première offre ?')
    ).toBeVisible()

    await page.pause()
    await page.getByRole('button', { name: 'Je le ferai plus tard' }).click()
    await expect(
      page.getByText('Bienvenue sur votre espace partenaire')
    ).toBeVisible()

    // I should be able to navigate without being redirected to onboarding
    await page.getByRole('link', { name: 'Réservations' }).click()
    await expect(
      page.getByRole('heading', { name: 'Réservations individuelles' })
    ).toBeVisible()
  })

  test('I should not be able to onboard me by submitting an Adage referencing file if I don’t have an Adage ID', async ({
    authenticatedPage: page,
  }) => {
    await page.getByLabel('Commencer la création d’offre sur ADAGE').click()
    await expect(
      page.getByRole('heading', { level: 1, name: 'Quelles sont les étapes ?' })
    ).toBeVisible()

    expect(
      page.getByRole('link', { name: /Déposer un dossier/ })
    ).toHaveAttribute('target', '_blank')
    expect(
      page.getByRole('link', { name: /Déposer un dossier/ })
    ).toHaveAttribute(
      'href',
      'https://demarche.numerique.gouv.fr/commencer/demande-de-referencement-sur-adage'
    )
    await page.getByRole('button', { name: /J’ai déposé un dossier/ }).click()
    await expect(
      page.getByText('Aucun dossier n’a été déposé par votre structure.')
    ).toBeVisible()
  })

  test('I should be able to onboard me by submitting an Adage referencing file if I have an Adage ID', async ({
    authenticatedPage: page,
  }) => {
    await page.getByLabel('Commencer la création d’offre sur ADAGE').click()
    await expect(
      page.getByRole('heading', { level: 1, name: 'Quelles sont les étapes ?' })
    ).toBeVisible()

    expect(
      page.getByRole('link', { name: /Déposer un dossier/ })
    ).toHaveAttribute('target', '_blank')
    expect(
      page.getByRole('link', { name: /Déposer un dossier/ })
    ).toHaveAttribute(
      'href',
      'https://demarche.numerique.gouv.fr/commencer/demande-de-referencement-sur-adage'
    )

    await page.route(/\/offerers\/\d+\/synchronize-onboarding$/, (route) =>
      route.fulfill({ status: 204 })
    )
    // At that point, the venue that was not onboarded is now mocked as being onboarded
    await page.route(/\/venues\/\d+$/, async (route) => {
      if (route.request().method() !== 'GET') {
        return route.continue()
      }
      const response = await route.fetch()
      const venue = await response.json()

      await route.fulfill({
        response,
        json: { ...venue, isOnboarded: true },
      })
    })

    await Promise.all([
      page.waitForResponse(isSynchronizeOffererOnboardingResponse),
      page.getByRole('button', { name: /J’ai déposé un dossier/ }).click(),
    ])

    await expect(page).toHaveURL(/\/accueil$/)
  })

  test('I should be able to create my first offer automatically', async ({
    authenticatedPage: page,
  }) => {
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

    await page.getByRole('link', { name: 'Automatiquement' }).click()

    await expect(
      page.getByRole('heading', {
        level: 1,
        name: 'Paramètres généraux',
      })
    ).toBeVisible()

    await expect(
      page.getByRole('heading', {
        level: 2,
        name: 'Informations administratives',
      })
    ).toBeVisible()
  })

  test('I should be able to start my first offer manually, saving and resume a draft offer, and publish it to get onboarded', async ({
    authenticatedPage: page,
  }) => {
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

    await page.getByRole('link', { name: 'Manuellement' }).click()

    await page.getByLabel(/Titre de l’offre/).fill('Mon offre en brouillon')
    await page.getByLabel('Catégorie').selectOption('Beaux-arts')
    await page.getByLabel(/Non accessible/).check()
    await page.getByText('Enregistrer et continuer').click()

    await Promise.all([
      page.goto('/onboarding/individuel'),
      page.waitForResponse(isGetCategoriesResponse),
      page.waitForResponse(isGetOffersResponse),
    ])

    await expect(
      page.getByRole('heading', {
        level: 2,
        name: 'Reprendre une offre déjà commencée',
      })
    ).toBeVisible()

    await Promise.all([
      page.waitForResponse(isGetOfferResponse),
      page.getByRole('link', { name: /Mon offre en brouillon/ }).click(),
    ])

    await expect(page.getByLabel(/Titre de l’offre/)).toHaveValue(
      'Mon offre en brouillon'
    )

    await Promise.all([
      page.waitForResponse(isPatchOffersResponse),
      page.getByText('Enregistrer et continuer').click(),
    ])

    await expect(
      page.getByRole('heading', { name: 'Où profiter de l’offre ?' })
    ).toBeVisible()

    await Promise.all([
      page.waitForResponse(isPatchOffersResponse),
      page.getByText('Enregistrer et continuer').click(),
    ])
    await expect(
      page.getByRole('heading', { name: 'Illustrez votre offre' })
    ).toBeVisible()
    await page.getByText('Enregistrer et continuer').click()
    await expect(page.getByRole('heading', { name: 'Tarifs' })).toBeVisible()
    await page.getByLabel(/Prix/).fill('42')
    await Promise.all([
      page.waitForResponse(isPatchStocksResponse),
      page.getByText('Enregistrer et continuer').click(),
    ])
    await expect(
      page.getByRole('heading', { name: 'Informations pratiques' })
    ).toBeVisible()
    await Promise.all([
      page.waitForResponse(isPatchOffersResponse),
      page.getByText('Enregistrer et continuer').click(),
    ])
    await expect(
      page.getByRole('heading', { level: 2, name: 'Description' })
    ).toBeVisible()
    await expect(page.getByText('Vous y êtes presque !')).toBeVisible()

    await Promise.all([
      page.waitForResponse(isGetOfferResponse),
      page.waitForResponse(isPublishOfferResponse),
      page.getByText('Publier l’offre').click(),
    ])

    await page
      .getByRole('dialog', {
        name: 'Félicitations, vous avez créé votre offre !',
      })
      .click()

    await page.getByRole('button', { name: 'Plus tard' }).click()

    await expect(
      page.getByText('Bienvenue sur votre espace partenaire')
    ).toBeVisible()
  })
})
