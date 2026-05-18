import { expect, test } from './fixtures/nonAttached'
import { checkAccessibility } from './helpers/accessibility'
import { navigateToAdministrationSpace } from './helpers/navigation'

test.describe('Non attached venue', () => {
  test('I should land on the non-attached venue page from the hub', async ({
    authenticatedPage: page,
  }) => {
    await page.goto('/hub')
    const venueButton = page
      .getByRole('button', { name: 'Mon Lieu non rattaché' })
      .last()

    await expect(venueButton).toBeVisible()
    await venueButton.click()
    await expect(page).toHaveURL('/rattachement-en-cours')
    await expect(
      page.getByText(
        'Votre rattachement est en cours de traitement par les équipes du pass Culture'
      )
    ).toBeVisible()
  })
  test('I should see the non attached banner in the admin space', async ({
    authenticatedPage: page,
  }) => {
    await page.goto('/hub')
    await navigateToAdministrationSpace(page)

    await checkAccessibility(page)
    await expect(
      page
        .getByRole('combobox', { name: 'Entité juridique' })
        .locator('option:checked')
    ).toHaveText('Offerer rattaché')
    await expect(
      page.getByText(
        "Les remboursements s'effectuent toutes les 2 à 3 semaines"
      )
    ).toBeVisible()

    await page
      .getByRole('combobox', { name: 'Entité juridique' })
      .selectOption({ label: 'Offerer non rattaché' })
    await expect(
      page.getByText(
        'Votre rattachement est en cours de traitement par les équipes du pass Culture'
      )
    ).toBeVisible()
  })
})
