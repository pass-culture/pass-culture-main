import { expect, request as playwrightRequest, test } from '@playwright/test'

import { login } from './helpers/auth'
import { BASE_API_URL, createNewProUser } from './helpers/sandbox'

const MOCKED_BACK_ADDRESS_LABEL = '3 Rue de Valois 75001 Paris'
const MOCKED_BACK_ADDRESS_STREET = '3 RUE DE VALOIS'

const newVenueName = 'First Venue'
const mySiret = '92345678912345'

interface Feature {
  name: string
  isActive: boolean
}

async function setFeatureFlags(
  requestContext: Awaited<ReturnType<typeof playwrightRequest.newContext>>,
  features: Feature[]
): Promise<void> {
  const response = await requestContext.patch(
    `${BASE_API_URL}/testing/features`,
    {
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      data: { features },
    }
  )
  expect(response.status()).toBe(204)
}

test.describe('Signup journey with not diffusible offerer siret', () => {
  test.beforeEach(async ({ page }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })

    const userData = await createNewProUser(requestContext)

    await setFeatureFlags(requestContext, [
      { name: 'WIP_IS_OPEN_TO_PUBLIC', isActive: true },
    ])

    await requestContext.dispose()

    await login(page, userData.user.email)
    await page.goto('/')
    await expect(page.getByTestId('spinner')).toHaveCount(0)
  })

  test('I should be able to sign up with a new account and create a new offerer with a not diffusible siret without an address', async ({
    page,
  }) => {
    await expect(page).toHaveURL(/\/inscription\/structure\/recherche/)
    await page.getByLabel(/Numéro de SIRET à 14 chiffres/).fill(mySiret)

    const venuesSiretPromise = page.waitForResponse(
      (response) =>
        response.url().includes('/venues/siret/') && response.status() === 200
    )
    await page.getByText('Continuer').click()
    await venuesSiretPromise

    await expect(page).toHaveURL(/\/inscription\/structure\/identification/)
    await expect(
      page.getByText(
        'Certaines informations de votre structure ne sont pas diffusibles.'
      )
    ).toBeVisible()
    await page.getByLabel(/Nom public/).fill(newVenueName)
    await page.getByLabel('Non').click()
    await expect(page.getByLabel(/Adresse postale/)).toHaveCount(0)

    await page.getByText('Étape suivante').click()
    await page.getByText('Étape précédente').click()
    await expect(page.getByLabel('Non')).toBeChecked()
    await page.getByText('Étape suivante').click()

    await expect(page).toHaveURL(/\/inscription\/structure\/activite/)
    await page.getByLabel(/Activité principale/).selectOption('Autre')
    await page.getByLabel('Numéro de téléphone').fill('612345678')
    await page.getByText('Au grand public').click()
    await page.getByText('Étape suivante').click()

    await expect(page).toHaveURL(/\/inscription\/structure\/confirmation/)

    const createOffererPromise = page.waitForResponse(
      (response) =>
        response.url().includes('/offerers/new') &&
        response.request().method() === 'POST'
    )
    await page.getByText('Valider et créer ma structure').click()
    await createOffererPromise

    await expect(
      page.getByLabel('Commencer la création d’offre sur l’application mobile')
    ).toBeVisible()
  })

  test('I should be able to sign up with a new account and create a new offerer with a not diffusible siret with an address', async ({
    page,
  }) => {
    await page.route(
      'https://data.geopf.fr/geocodage/search/?limit=5&q=*',
      (route) => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            type: 'FeatureCollection',
            version: 'draft',
            features: [
              {
                type: 'Feature',
                geometry: {
                  type: 'Point',
                  coordinates: [2.3056966, 48.8716934],
                },
                properties: {
                  label: MOCKED_BACK_ADDRESS_LABEL,
                  score: 0.97351,
                  housenumber: '89',
                  id: '75108_5194_00089',
                  name: MOCKED_BACK_ADDRESS_STREET,
                  postcode: '75008',
                  citycode: '75108',
                  x: 649261.94,
                  y: 6863742.69,
                  city: 'Paris',
                  district: 'Paris 8e Arrondissement',
                  context: '75, Paris, Île-de-France',
                  type: 'housenumber',
                  importance: 0.70861,
                  street: MOCKED_BACK_ADDRESS_STREET,
                },
              },
            ],
            attribution: 'BAN',
            licence: 'ETALAB-2.0',
            query: MOCKED_BACK_ADDRESS_LABEL,
            limit: 5,
          }),
        })
      }
    )

    await expect(page).toHaveURL(/\/inscription\/structure\/recherche/)
    await page.getByLabel(/Numéro de SIRET à 14 chiffres/).fill(mySiret)

    const venuesSiretPromise = page.waitForResponse(
      (response) =>
        response.url().includes('/venues/siret/') && response.status() === 200
    )
    await page.getByText('Continuer').click()
    await venuesSiretPromise

    await expect(page).toHaveURL(/\/inscription\/structure\/identification/)
    await page.getByLabel(/Nom public/).fill(newVenueName)
    await page.getByText('Oui').click()

    const addressSearchPromise = page.waitForResponse((response) =>
      response.url().includes('data.geopf.fr/geocodage/search')
    )
    await page.getByLabel(/Adresse postale/).fill(MOCKED_BACK_ADDRESS_LABEL)
    await addressSearchPromise
    await page.getByTestId('list').getByText(MOCKED_BACK_ADDRESS_LABEL).click()

    await page.getByText('Étape suivante').click()
    await page.getByText('Étape précédente').click()
    await page.getByLabel('Oui').click()
    await page.getByText('Étape suivante').click()

    await expect(page).toHaveURL(/\/inscription\/structure\/activite/)
    await page.getByLabel(/Activité principale/).selectOption('Galerie d’art')
    await page.getByLabel('Numéro de téléphone').fill('612345678')
    await page.getByText('Au grand public').click()
    await page.getByText('Étape suivante').click()

    await expect(page).toHaveURL(/\/inscription\/structure\/confirmation/)

    const createOffererPromise = page.waitForResponse(
      (response) =>
        response.url().includes('/offerers/new') &&
        response.request().method() === 'POST'
    )
    await page.getByText('Valider et créer ma structure').click()
    await createOffererPromise

    await expect(
      page.getByLabel('Commencer la création d’offre sur l’application mobile')
    ).toBeVisible()
  })
})
