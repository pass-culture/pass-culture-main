import { expect, type Page } from '@playwright/test'

export async function navigateToHubAndPickVenue(page: Page, venueName: string) {
  await page.goto('/hub')
  await expect(
    page.getByRole('heading', {
      name: 'À quelle structure souhaitez-vous accéder ?',
    })
  ).toBeVisible()

  const venueButton = page.getByRole('button', { name: venueName }).first()

  await expect(venueButton).toBeVisible()
  await venueButton.click()
  await page.waitForURL(/\/accueil$/)
}

export async function joinExistingVenueSpace(page: Page, siret: string) {
  await page.goto('/inscription/structure/recherche')
  await expect(page).toHaveURL(/\/inscription\/structure\/recherche/)
  await page.getByLabel(/Numéro de SIRET à 14 chiffres/).fill(siret)

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

  await page.getByText('Accéder à votre espace').click()
}
