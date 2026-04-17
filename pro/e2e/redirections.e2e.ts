import { expect, test } from '@playwright/test'

test.describe('Redirections', () => {
  test('`/` path redirections', async ({ page }) => {
    await page.goto('/')
    await expect(
      page.getByRole('heading', { name: 'Connectez-vous' })
    ).toBeVisible()
  })
  test('`/inscription` path redirections', async ({ page }) => {
    await page.goto('/inscription')
    await expect(
      page.getByRole('heading', {
        name: 'Commençons par identifier votre profil',
      })
    ).toBeVisible()
  })
})
