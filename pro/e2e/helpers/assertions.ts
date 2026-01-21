import { expect, type Page } from '@playwright/test'

export async function expectSuccessSnackbar(
  page: Page,
  message: string
): Promise<void> {
  await expect(
    page
      .locator('[data-testid^="global-snack-bar-success"]')
      .filter({ hasText: message })
  ).toBeVisible()
}
