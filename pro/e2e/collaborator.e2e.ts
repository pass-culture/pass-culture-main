import { randomUUID } from 'node:crypto'
import AxeBuilder from '@axe-core/playwright'
import { expect, request as playwrightRequest, test } from '@playwright/test'

import { expectSuccessSnackbar } from './helpers/assertions'
import { loginAndNavigate } from './helpers/auth'
import { BASE_API_URL, sandboxCall } from './helpers/sandbox'

interface ProUserResponse {
  user: {
    email: string
  }
}

interface EmailResponse {
  To: string
  params: {
    OFFERER_NAME: string
  }
}

test.describe('Collaborator list feature', () => {
  test('I can add a new collaborator and he receives an email invitation', async ({
    page,
  }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })

    const userData = await sandboxCall<ProUserResponse>(
      requestContext,
      'GET',
      `${BASE_API_URL}/sandboxes/pro/create_regular_pro_user_already_onboarded`
    )
    const userEmail = userData.user.email

    const clearResponse = await requestContext.fetch(
      `${BASE_API_URL}/sandboxes/clear_email_list`,
      { method: 'GET' }
    )
    expect(clearResponse.status()).toBe(200)

    await requestContext.dispose()

    const randomEmail = `collaborator${randomUUID()}@example.com`

    await loginAndNavigate(page, userEmail, '/accueil')

    await page.getByText('Collaborateurs').click()

    await expect(page).toHaveURL(/\/collaborateurs/)
    await expect(page.getByTestId('spinner')).toHaveCount(0)
    await expect(page.getByText(userEmail)).toBeVisible()

    const accessibilityResults = await new AxeBuilder({ page }).analyze()
    expect(accessibilityResults.violations).toHaveLength(0)

    await page.getByText('Ajouter un collaborateur').click()
    await page.getByLabel('Adresse email').fill(randomEmail)
    await page.getByRole('button', { name: 'Inviter' }).click()

    await expectSuccessSnackbar(page, "L'invitation a bien été envoyée.")

    await expect(page.getByTestId('spinner')).toHaveCount(0)

    const newCollaboratorRow = page
      .getByRole('row')
      .filter({ hasText: randomEmail })
    await expect(newCollaboratorRow).toContainText('En attente')

    const currentUserRow = page.getByRole('row').filter({ hasText: userEmail })
    await expect(currentUserRow).toContainText('Validé')

    const emailRequestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })

    const emailData = await sandboxCall<EmailResponse>(
      emailRequestContext,
      'GET',
      `${BASE_API_URL}/sandboxes/get_unique_email`
    )

    expect(emailData.To).toBe(randomEmail)
    expect(emailData.params.OFFERER_NAME).toContain(
      'Le Petit Rintintin Management'
    )

    await emailRequestContext.dispose()
  })
})
