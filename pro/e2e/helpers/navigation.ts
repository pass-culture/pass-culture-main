import { expect, type Page } from '@playwright/test'

export async function navigateToAdministrationSpace(page: Page) {
  await page.getByRole('link', { name: /Espace administration/ }).click()

  await expect(page).toHaveURL(/\/administration\/remboursements($|\?.*)/)
  await expect(
    page.getByRole('heading', { level: 1, name: 'Gestion financière' })
  ).toBeVisible()
  await expect(page.getByTestId('spinner')).toHaveCount(0)
}
