import { expect, request as playwrightRequest, test } from '@playwright/test'

import { login } from './helpers/auth'
import { BASE_API_URL, sandboxCall } from './helpers/sandbox'

interface ProUserResponse {
  user: {
    email: string
  }
}

test.describe('Switch Offerer and Venue', () => {
  test('I should be redirected to the onboarding page when I switch to an offerer not onboarded yet', async ({
    page,
  }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })

    const userData = await sandboxCall<ProUserResponse>(
      requestContext,
      'GET',
      `${BASE_API_URL}/sandboxes/pro/create_pro_user_with_1_onboarded_and_1_unonboarded_offerers`
    )
    const userEmail = userData.user.email

    await requestContext.dispose()

    await login(page, userEmail)

    await page.goto('/offres')

    await expect(
      page.getByRole('heading', { level: 1, name: 'Offres individuelles' })
    ).toBeVisible()

    await page.getByTestId('offerer-select').click()
    await page.getByText(/Changer/).click()
    await page
      .getByTestId('offerers-selection-menu')
      .getByText('Unonboarded Offerer')
      .click()
    await expect(page.getByTestId('header-dropdown-menu-div')).toHaveCount(0)
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await expect(
      page.getByRole('heading', {
        level: 1,
        name: 'Bienvenue sur le pass Culture Pro !',
      })
    ).toBeVisible()

    await expect(
      page.getByRole('heading', {
        level: 2,
        name: 'Où souhaitez-vous diffuser votre première offre ?',
      })
    ).toBeVisible()
  })
})
