import { expect, request as playwrightRequest, test } from '@playwright/test'

import { checkAccessibility } from './helpers/accessibility'
import { MOCKED_BACK_ADDRESS_LABEL, mockAddressSearch } from './helpers/address'
import { doLogin } from './helpers/auth'
import {
  BASE_API_URL,
  createNewProUser,
  createNewProUserAndCollectivityOffererWithVenue,
  createNewProUserAndOfferer,
  createNewProUserAndOffererWithVenue,
} from './helpers/sandbox'

const newVenueName = 'First Venue'

test.describe('Signup journey with unknown offerer and unknown venue', () => {
  const mySiret = '12345678912345'

  test('I should be able to sign up with a new account and create a new offerer with an unknown SIREN (unknown SIRET)', async ({
    page,
  }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const userData = await createNewProUser(requestContext)
    await requestContext.dispose()

    await doLogin(page, userData.user.email, { retry: true })
    await page.goto('/')
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await expect(page).toHaveURL(/\/inscription\/structure\/recherche/)
    await checkAccessibility(page)
    await page.getByLabel(/Numéro de SIRET à 14 chiffres/).fill(mySiret)

    const venuesSiretPromise = page.waitForResponse(
      (response) =>
        response.url().includes('/venues/siret/') && response.status() === 200
    )
    await page.getByText('Continuer').click()
    await venuesSiretPromise

    await expect(page).toHaveURL(/\/inscription\/structure\/identification/)
    await checkAccessibility(page)
    await page.getByLabel('Nom public').fill(newVenueName)
    // Make the venue open to public
    await page.getByText('Oui').click()

    await page.getByText('Continuer').click()

    await checkAccessibility(page)

    // I fill activity form without target audience
    await expect(page).toHaveURL(/\/inscription\/structure\/activite/)
    await page.getByLabel(/Activité principale/).selectOption('Galerie d’art')
    await page.getByLabel('Numéro de téléphone').fill('612345678')
    await page
      .getByLabel('Site internet, réseau social')
      .fill('http://example.com')
    await page.getByText('Continuer').click()
    await expect(
      page.getByText('Veuillez sélectionner au moins une option')
    ).toBeVisible()

    await expect(page).toHaveURL(/\/inscription\/structure\/activite/)
    await page.getByText('Aux jeunes via l’application pass Culture').click()
    await checkAccessibility(page)
    await page.getByText('Continuer').click()

    await expect(page).toHaveURL(/\/inscription\/structure\/confirmation/)
    await expect(page.getByText('5 Rue Curial, 75019 Paris')).toBeVisible()
    await checkAccessibility(page)

    const createOffererPromise = page.waitForResponse(
      (response) =>
        response.url().includes('/offerers/new') &&
        response.request().method() === 'POST'
    )
    await page.getByText('Valider et créer ma structure').click()
    await createOffererPromise

    await expect(page.getByTestId('spinner')).toHaveCount(0)
    await expect(
      page.getByText('Où souhaitez-vous diffuser votre première offre ?')
    ).toBeVisible()
  })

  test('I should be able to sign up with a new account and create a new offerer with an unknown SIREN (unknown SIRET) and a custom address', async ({
    page,
  }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })
    const userData = await createNewProUser(requestContext)
    await requestContext.dispose()

    await mockAddressSearch(page)

    await doLogin(page, userData.user.email, { retry: true })
    await page.goto('/')
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await page.getByLabel(/Numéro de SIRET à 14 chiffres/).fill(mySiret)

    const venuesSiretPromise = page.waitForResponse(
      (response) =>
        response.url().includes('/venues/siret/') && response.status() === 200
    )
    await page.getByText('Continuer').click()
    await venuesSiretPromise

    await page.getByLabel('Nom public').fill(newVenueName)
    await page.getByText('Oui').click()

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

    await page.getByText('Continuer').click()

    await expect(page).toHaveURL(/\/inscription\/structure\/activite/)
    await page.getByLabel(/Activité principale/).selectOption('Galerie d’art')
    await page.getByLabel('Numéro de téléphone').fill('612345678')
    await page
      .getByLabel('Site internet, réseau social')
      .fill('http://example.com')
    await page.getByText('Aux jeunes via l’application pass Culture').click()
    await page.getByText('Continuer').click()

    await expect(page).toHaveURL(/\/inscription\/structure\/confirmation/)
    await expect(page.getByText('10 Rue du test, 75002 Paris')).toBeVisible()

    const createOffererPromise = page.waitForResponse(
      (response) =>
        response.url().includes('/offerers/new') &&
        response.request().method() === 'POST'
    )
    await page.getByText('Valider et créer ma structure').click()
    await createOffererPromise

    // the offerer is created
    await expect(page.getByTestId('spinner')).toHaveCount(0)
    await expect(
      page.getByText('Où souhaitez-vous diffuser votre première offre ?')
    ).toBeVisible()
  })
})

test.describe('Signup journey with known offerer...', () => {
  test.describe('...and unknown venue', () => {
    const endSiret = '12345'

    test('I should be able to sign up with a new account and create a new venue with a known SIREN (unknown SIRET)', async ({
      page,
    }) => {
      const requestContext = await playwrightRequest.newContext({
        baseURL: BASE_API_URL,
      })
      const userData = await createNewProUserAndOfferer(requestContext)
      const mySiret = userData.siren + endSiret
      await requestContext.dispose()

      await doLogin(page, userData.user.email, { retry: true })
      await page.goto('/')
      await expect(page.getByTestId('spinner')).toHaveCount(0)

      await expect(page).toHaveURL(/\/inscription\/structure\/recherche/)
      await page.getByLabel(/Numéro de SIRET à 14 chiffres/).fill(mySiret)

      const venuesSiretPromise = page.waitForResponse(
        (response) =>
          response.url().includes('/venues/siret/') && response.status() === 200
      )
      await page.getByText('Continuer').click()
      await venuesSiretPromise

      await expect(page).toHaveURL(/\/inscription\/structure\/identification/)
      await page.getByLabel('Nom public').fill(newVenueName)
      // Make the venue open to public
      await page.getByText('Oui').click()

      await page.getByText('Continuer').click()

      await expect(page).toHaveURL(/\/inscription\/structure\/activite/)
      await page.getByLabel(/Activité principale/).selectOption('Galerie d’art')
      await page.getByLabel('Numéro de téléphone').fill('612345678')
      await page
        .getByLabel('Site internet, réseau social')
        .fill('http://example.com')
      await page.getByText('Aux jeunes via l’application pass Culture').click()
      await page.getByText('Continuer').click()

      await expect(page).toHaveURL(/\/inscription\/structure\/confirmation/)

      const createOffererPromise = page.waitForResponse(
        (response) =>
          response.url().includes('/offerers/new') &&
          response.request().method() === 'POST'
      )
      await page.getByText('Valider et créer ma structure').click()
      await createOffererPromise

      await expect(page.getByTestId('spinner')).toHaveCount(0)
      await expect(page).toHaveURL('/rattachement-en-cours')
      await expect(
        page.getByText(
          'Votre rattachement est en cours de traitement par les équipes du pass Culture'
        )
      ).toBeVisible()
    })
  })

  test.describe('...and known venue', () => {
    test('I should be able as a local authority to sign up with a new account and a known offerer/venue and then create a new venue in the space', async ({
      page,
    }) => {
      const requestContext = await playwrightRequest.newContext({
        baseURL: BASE_API_URL,
      })
      const userData =
        await createNewProUserAndCollectivityOffererWithVenue(requestContext)
      const mySiret = userData.siret
      await requestContext.dispose()

      await mockAddressSearch(page)

      await doLogin(page, userData.user.email, { retry: true })

      await expect(page).toHaveURL(/\/inscription\/structure\/recherche$/)
      await page.getByLabel(/Numéro de SIRET à 14 chiffres/).fill(mySiret)

      const venuesSiretPromise = page.waitForResponse(
        (response) =>
          response.url().includes('/venues/siret/') && response.status() === 200
      )
      await page.getByText('Continuer').click()
      await venuesSiretPromise

      await expect(page).toHaveURL(/\/inscription\/structure\/rattachement$/)

      const addressSearchPromise = page.waitForResponse((response) =>
        response.url().includes('data.geopf.fr/geocodage/search')
      )
      await page
        .getByRole('button', { name: 'Ajouter une nouvelle structure' })
        .click()
      await addressSearchPromise

      await expect(page).toHaveURL(/\/inscription\/structure\/identification$/)
      await page.getByLabel(/Adresse postale/).clear()
      await page.getByLabel(/Adresse postale/).fill(MOCKED_BACK_ADDRESS_LABEL)

      const addressSearchPromise2 = page.waitForResponse((response) =>
        response.url().includes('data.geopf.fr/geocodage/search')
      )
      await addressSearchPromise2
      await page
        .getByRole('option', { name: MOCKED_BACK_ADDRESS_LABEL })
        .click()
      // Make the venue open to public
      await page.getByText('Oui').click()

      await page.getByText('Continuer').click()

      await expect(page).toHaveURL(/\/inscription\/structure\/activite$/)
      await page
        .getByLabel(/Activité principale/)
        .selectOption('Sélectionnez votre activité principale')
      await page.getByLabel('Numéro de téléphone').fill('612345678')
      await page
        .getByLabel('Site internet, réseau social')
        .fill('http://example.com')
      await page.getByText('Aux jeunes via l’application pass Culture').click()
      await page.getByText('Continuer').click()
      await expect(page.getByText('Activité non valide')).toBeVisible()

      await expect(page).toHaveURL(/\/inscription\/structure\/activite/)
      await page.getByLabel(/Activité principale/).selectOption('Galerie d’art')
      await page.getByText('Continuer').click()

      await expect(page).toHaveURL(/\/inscription\/structure\/confirmation$/)

      const createOffererPromise = page.waitForResponse(
        (response) =>
          response.url().includes('/offerers/new') &&
          response.request().method() === 'POST'
      )
      await page.getByText('Valider et créer ma structure').click()
      await createOffererPromise

      await expect(page.getByTestId('spinner')).toHaveCount(0)
      await expect(page).toHaveURL('/hub')
      await expect(
        page.getByRole('heading', {
          name: 'À quelle structure souhaitez-vous accéder ?',
        })
      ).toBeVisible()
      await expect(page.getByText(/3 rue de valois/i)).toBeVisible()
    })

    test('I should be able to sign up with a new account and a known offerer/venue and then join the space', async ({
      page,
    }) => {
      const requestContext = await playwrightRequest.newContext({
        baseURL: BASE_API_URL,
      })
      const userData = await createNewProUserAndOffererWithVenue(requestContext)
      const mySiret = userData.siret
      await requestContext.dispose()

      await mockAddressSearch(page)

      await doLogin(page, userData.user.email, { retry: true })
      await page.goto('/')
      await expect(page.getByTestId('spinner')).toHaveCount(0)

      await expect(page).toHaveURL(/\/inscription\/structure\/recherche/)
      await page.getByLabel(/Numéro de SIRET à 14 chiffres/).fill(mySiret)

      const venuesSiretPromise = page.waitForResponse(
        (response) =>
          response.url().includes('/venues/siret/') && response.status() === 200
      )
      await page.getByText('Continuer').click()
      await venuesSiretPromise

      await page.getByText('Rejoindre cet espace').click()

      const postOfferersPromise = page.waitForResponse(
        (response) =>
          response.url().includes('/offerers') &&
          response.request().method() === 'POST' &&
          response.status() === 201
      )
      await page.getByTestId('confirm-dialog-button-confirm').click()
      await postOfferersPromise

      await page.getByText('Accéder à mon espace').click()

      await expect(page).toHaveURL('/rattachement-en-cours')
      await expect(
        page.getByText(
          'Votre rattachement est en cours de traitement par les équipes du pass Culture'
        )
      ).toBeVisible()
    })
  })
})
