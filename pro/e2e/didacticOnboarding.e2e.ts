import { expect, test } from './fixtures/didacticOnboarding'
import {
  isGetCategoriesResponse,
  isGetEligibilityResponse,
  isGetOfferResponse,
  isGetOffersResponse,
  isPatchOffersResponse,
  isPatchStocksResponse,
  isPublishOfferResponse,
} from './helpers/requests'

test.describe('Didactic Onboarding feature', () => {
  test.beforeEach(async ({ authenticatedPage: page }) => {
    await page.goto('/accueil')
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

    // Press tab to focus on the top of the page
    await page.keyboard.press('Tab')
    await page.getByRole('link', { name: 'Aller au contenu' }).click()
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
    await page.route(/\/offerers\/(\d+)\/eligibility/, (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          offererId: route
            .request()
            .url()
            .match(/\/offerers\/(\d+)\//)![1],
          hasAdageId: true,
          hasDsApplication: null,
          isOnboarded: true,
        }),
      })
    })

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
    await Promise.all([
      page.waitForResponse(isGetEligibilityResponse),
      page.getByRole('button', { name: /J’ai déposé un dossier/ }).click(),
    ])

    await expect(
      page.getByText(/Votre page partenaire|Vos pages partenaire/)
    ).toBeVisible()
    await expect(page.url().includes('/accueil')).toBeTruthy()
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
        name: 'Gestion des synchronisations',
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

    await page.goto('/onboarding/individuel')
    await Promise.all([
      page.waitForResponse(isGetOffersResponse),
      page.waitForResponse(isGetCategoriesResponse),
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
