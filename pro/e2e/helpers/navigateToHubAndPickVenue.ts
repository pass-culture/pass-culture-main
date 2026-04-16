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
