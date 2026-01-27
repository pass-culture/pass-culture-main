import { expect, request as playwrightRequest, test } from '@playwright/test'

import { checkAccessibility } from './helpers/accessibility'
import { expectSuccessSnackbar } from './helpers/assertions'
import { login } from './helpers/auth'
import { BASE_API_URL, sandboxCall } from './helpers/sandbox'

interface ProUserWithFinancialDataResponse {
  user: {
    email: string
  }
}

interface ProUserWithVenuesResponse {
  user: {
    email: string
  }
}

test.describe('Financial Management - messages, links to external help page, reimbursement details, unattach (Optimized)', () => {
  test('I should see information message about reimbursement', async ({
    page,
  }) => {
    const requestContext = await playwrightRequest.newContext({
      baseURL: BASE_API_URL,
    })

    const userData = await sandboxCall<ProUserWithFinancialDataResponse>(
      requestContext,
      'GET',
      `${BASE_API_URL}/sandboxes/pro/create_pro_user_with_financial_data`
    )

    await requestContext.dispose()

    await login(page, userData.user.email)
    await page.goto('/remboursements')
    await expect(page.getByTestId('spinner')).toHaveCount(0)

    await expect(
      page.getByText(
        "Les remboursements s'effectuent toutes les 2 à 3 semaines"
      )
    ).toBeVisible()
    await expect(
      page.getByText(
        'Nous remboursons en un virement toutes les réservations validées entre le 1ᵉʳ et le 15 du mois, et lors d’un second toutes celles validées entre le 16 et le 31 du mois.'
      )
    ).toBeVisible()
    await expect(
      page.getByText(
        'Les offres de type événement se valident automatiquement 48h à 72h après leur date de réalisation, leurs remboursements peuvent se faire sur la quinzaine suivante.'
      )
    ).toBeVisible()

    await expect(page.getByTestId('spinner')).toHaveCount(0)
    await expect(page.getByTestId('invoice-title-row')).toHaveCount(0)
    await expect(page.getByTestId('invoice-item-row')).toHaveCount(0)
    await expect(
      page.getByText(
        'Vous n’avez pas encore de justificatifs de remboursement disponibles'
      )
    ).toBeVisible()

    await checkAccessibility(page)

    const nextReimbursementLink = page.getByText(
      /En savoir plus sur les prochains remboursements/
    )
    const nextReimbursementHref =
      await nextReimbursementLink.getAttribute('href')
    expect(nextReimbursementHref).toContain('4411992051601')

    const termsLink = page.getByText(/Connaître les modalités de remboursement/)
    const termsHref = await termsLink.getAttribute('href')
    expect(termsHref).toContain('4412007300369')
  })

  test.describe('Data contains 1 offerer with 3 venues', () => {
    test.beforeEach(async ({ page }) => {
      const requestContext = await playwrightRequest.newContext({
        baseURL: BASE_API_URL,
      })

      const userData = await sandboxCall<ProUserWithVenuesResponse>(
        requestContext,
        'GET',
        `${BASE_API_URL}/sandboxes/pro/create_pro_user_with_financial_data_and_3_venues`
      )

      await requestContext.dispose()

      await login(page, userData.user.email)
      await page.goto('/remboursements/informations-bancaires')
      await expect(page.getByTestId('profile-button')).toBeVisible()
      await expect(page.getByTestId('spinner')).toHaveCount(0)
    })

    test('I should be able to attach and unattach a few venues', async ({
      page,
    }) => {
      await page.getByText('Rattacher une structure').click()

      const dialog = page.getByRole('dialog')
      await dialog.getByText('Tout sélectionner').click()
      await dialog.getByText('Enregistrer').click()

      await expectSuccessSnackbar(
        page,
        'Vos modifications ont bien été prises en compte.'
      )
      await expect(page.getByRole('dialog')).toHaveCount(0)

      const linkedVenuesSection = page.getByTestId(
        'reimbursement-bank-account-linked-venues'
      )
      await expect(
        linkedVenuesSection.getByText(
          'Structures rattachées à ce compte bancaire'
        )
      ).toBeVisible()
      await expect(linkedVenuesSection.getByText('Mon lieu 1')).toBeVisible()
      await expect(linkedVenuesSection.getByText('Mon lieu 2')).toBeVisible()
      await expect(linkedVenuesSection.getByText('Mon lieu 3')).toBeVisible()
      await linkedVenuesSection.getByText('Modifier').click()

      const modifyDialog = page.getByRole('dialog')
      await modifyDialog.getByText('Mon lieu 1').click()
      await modifyDialog.getByText('Mon lieu 2').click()
      await modifyDialog.getByText('Enregistrer').click()
      await expect(
        modifyDialog.getByText(
          'Attention : la ou les structures désélectionnées ne seront plus remboursées sur ce compte bancaire'
        )
      ).toBeVisible()
      await modifyDialog.getByText('Confirmer').click()

      await expectSuccessSnackbar(
        page,
        'Vos modifications ont bien été prises en compte.'
      )
      await expect(page.getByRole('dialog')).toHaveCount(0)

      await expect(
        linkedVenuesSection.getByText(
          'Structure rattachée à ce compte bancaire'
        )
      ).toBeVisible()
      await expect(
        linkedVenuesSection.getByText(
          'Certaines de vos structures ne sont pas rattachées.'
        )
      ).toBeVisible()
      await expect(linkedVenuesSection.getByText('Mon lieu 3')).toBeVisible()
      await expect(linkedVenuesSection.getByText('Mon lieu 1')).toHaveCount(0)
      await expect(linkedVenuesSection.getByText('Mon lieu 2')).toHaveCount(0)
    })

    test('I should be able to attach and unattach all venues', async ({
      page,
    }) => {
      await page.getByText('Rattacher une structure').click()

      const dialog = page.getByRole('dialog')
      await dialog.getByText('Tout sélectionner').click()
      await dialog.getByText('Enregistrer').click()

      await expectSuccessSnackbar(
        page,
        'Vos modifications ont bien été prises en compte.'
      )
      await expect(page.getByRole('dialog')).toHaveCount(0)

      await expect(
        page.getByText('Structures rattachées à ce compte bancaire')
      ).toBeVisible()
      await page.getByText('Modifier').click()

      const modifyDialog = page.getByRole('dialog')
      await modifyDialog.getByText('Tout désélectionner').click()
      await modifyDialog.getByText('Enregistrer').click()
      await expect(
        modifyDialog.getByText(
          'Attention : la ou les structures désélectionnées ne seront plus remboursées sur ce compte bancaire'
        )
      ).toBeVisible()
      await modifyDialog.getByText('Confirmer').click()

      await expectSuccessSnackbar(
        page,
        'Vos modifications ont bien été prises en compte.'
      )
      await expect(page.getByRole('dialog')).toHaveCount(0)

      const linkedVenuesSection = page.getByTestId(
        'reimbursement-bank-account-linked-venues'
      )
      await expect(
        linkedVenuesSection.getByText(
          'Structure rattachée à ce compte bancaire'
        )
      ).toBeVisible()
      await expect(
        linkedVenuesSection.getByText(
          'Aucune structure n’est rattachée à ce compte bancaire.'
        )
      ).toBeVisible()
      await expect(linkedVenuesSection.getByText('Mon lieu 1')).toHaveCount(0)
      await expect(linkedVenuesSection.getByText('Mon lieu 2')).toHaveCount(0)
      await expect(linkedVenuesSection.getByText('Mon lieu 3')).toHaveCount(0)
    })
  })
})
