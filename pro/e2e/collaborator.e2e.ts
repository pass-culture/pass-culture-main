import { randomUUID } from 'node:crypto'
import { expect, request as playwrightRequest, test } from '@playwright/test'

import { checkAccessibility } from './helpers/accessibility'
import { expectSuccessSnackbar } from './helpers/assertions'
import { login } from './helpers/auth'
import { navigateToAdministrationSpace } from './helpers/navigation'
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

    const clearResponse = await requestContext.fetch(
      `${BASE_API_URL}/sandboxes/clear_email_list`,
      { method: 'GET', headers: { 'x-api-key': process.env.E2E_API_KEY } }
    )
    expect(clearResponse.status()).toBe(200)

    await requestContext.dispose()

    const randomEmail = `collaborator${randomUUID()}@example.com`

    await login(page, userData.user.email)
    await navigateToAdministrationSpace(page)
    await page.getByRole('link', { name: 'Collaborateurs' }).click()
    await expect(page).toHaveURL(/\/administration\/collaborateurs$/)

    await checkAccessibility(page)

    await page.getByText('Ajouter un collaborateur').click()
    await page.getByLabel('Adresse email').fill(randomEmail)
    await page.getByRole('button', { name: 'Inviter' }).click()

    await expectSuccessSnackbar(page, "L'invitation a bien été envoyée.")

    await expect(page.getByTestId('spinner')).toHaveCount(0)

    const newCollaboratorRow = page
      .getByRole('row')
      .filter({ hasText: randomEmail })
    await expect(newCollaboratorRow).toContainText('En attente')

    const currentUserRow = page
      .getByRole('row')
      .filter({ hasText: userData.user.email })
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
