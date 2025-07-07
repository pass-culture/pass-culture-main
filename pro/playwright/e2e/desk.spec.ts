import { test, expect } from '@playwright/test'
import { addDays, format } from 'date-fns'

import { loginAndGoToPage, sandboxCall } from '../support/helpers'

// Use .serial() to ensure tests run in order, as they share state (tokens).
test.describe.serial('Desk (Guichet) feature', () => {
  // let page: Page
  let body: any

  let tokenConfirmed: string
  let tokenTooSoon: string
  let tokenUsed: string
  let tokenCanceled: string
  let tokenReimbursed: string
  let tokenOther: string

  test.beforeAll(async ({ request }) => {
    // Create user and get tokens via API call
    const response = await sandboxCall(
      request,
      'GET',
      'http://localhost:5001/sandboxes/pro/create_pro_user_with_bookings'
    )
    body = await response.json()
    tokenConfirmed = body.tokenConfirmed
    tokenTooSoon = body.tokenTooSoon
    tokenUsed = body.tokenUsed
    tokenCanceled = body.tokenCanceled
    tokenReimbursed = body.tokenReimbursed
    tokenOther = body.tokenOther

    // page = await browser.newPage()
    // await loginAndGoToPage(page, body.user.email, "/guichet")
  })

  test('I should see help information on desk page', async ({ page, context }) => {
    await loginAndGoToPage(page, body.user.email, "/guichet")

    await test.step('The identity check message is displayed', async () => {
      await expect(page.getByText('N’oubliez pas de vérifier l’identité du bénéficiaire avant de valider la contremarque.')).toBeVisible()
      await expect(page.getByText('Les pièces d’identité doivent impérativement être présentées physiquement. Merci de ne pas accepter les pièces d’identité au format numérique.')).toBeVisible()
    })

    await test.step('I can click and open the "Modalités de retrait et CGU" page', async () => {
      const newTabPagePromise = context.waitForEvent('page')
      await page.getByText('Modalités de retrait et CGU').click()
      const newTabPage = await newTabPagePromise
      await newTabPage.waitForLoadState()

      expect(newTabPage.url()).toContain('aide.passculture.app')
      expect(newTabPage.url()).toContain('Acteurs-Culturels-Modalit%C3%A9s-de-retrait-et-CGU')
    })
  })

  test('I should be able to validate a valid countermark', async ({ page }) => {
    await loginAndGoToPage(page, body.user.email, "/guichet")

    await test.step(`I add a valid countermark ${tokenConfirmed}`, async () => {
      await page.getByLabel('Contremarque').fill(tokenConfirmed)
      await expect(page.getByText('Coupon vérifié, cliquez sur "Valider" pour enregistrer')).toBeVisible()
    })

    await test.step('I validate the countermark and see confirmation', async () => {
      await page.getByRole('button', { name: 'Valider la contremarque' }).click()
      await expect(page.getByText('Contremarque validée !')).toBeVisible()
    })
  })

  test('It should decline a non-valid countermark', async ({ page }) => {
    await loginAndGoToPage(page, body.user.email, "/guichet")

    await test.step('I add this countermark "XXXXXX"', async () => {
      await page.getByLabel('Contremarque').fill('XXXXXX')
    })

    await test.step('the countermark is rejected as invalid', async () => {
      await expect(page.getByTestId('desk-message')).toHaveText("La contremarque n'existe pas")
      await expect(page.getByRole('button', { name: 'Valider la contremarque' })).toBeDisabled()
    })
  })

  test('It should decline an event countermark more than 48h before', async ({ page }) => {
    await loginAndGoToPage(page, body.user.email, "/guichet")

    await test.step(`I add this countermark "${tokenTooSoon}"`, async () => {
      await page.getByLabel('Contremarque').fill(tokenTooSoon)
    })

    await test.step('the countermark is rejected as invalid', async () => {
      const date = format(addDays(new Date(), 2), 'dd/MM/yyyy')
      const expectedText = `Vous pourrez valider cette contremarque à partir du ${date}`

      await expect(page.getByTestId('desk-message')).toContainText(expectedText)
      await expect(page.getByTestId('desk-message')).toContainText('une fois le délai d’annulation passé.')
      await expect(page.getByRole('button', { name: 'Valider la contremarque' })).toBeDisabled()
    })
  })

  test('I should be able to invalidate an already used countermark', async ({ page }) => {
    await loginAndGoToPage(page, body.user.email, "/guichet")

    await test.step(`I add this countermark "${tokenUsed}"`, async () => {
      await page.getByLabel('Contremarque').fill(tokenUsed)
      await expect(page.getByText(/Cette contremarque a été validée./)).toBeVisible()
    })

    await test.step('I invalidate the countermark', async () => {
      await page.getByRole('button', { name: 'Invalider la contremarque' }).click()
      await page.getByRole('button', { name: 'Continuer' }).click()
    })

    await test.step('The countermark is invalidated', async () => {
      await expect(page.getByText('Contremarque invalidée !')).toBeVisible()
    })
  })

  test('I should not be able to validate another pro countermark', async ({ page }) => {
    await loginAndGoToPage(page, body.user.email, "/guichet")

    await test.step(`I add this countermark "${tokenOther}"`, async () => {
      await page.getByLabel('Contremarque').fill(tokenOther)
    })

    await test.step('I cannot validate the countermark', async () => {
      await expect(page.getByText("Vous n'avez pas les droits nécessaires pour voir cette contremarque")).toBeVisible()
      await expect(page.getByRole('button', { name: 'Valider la contremarque' })).toBeDisabled()
    })
  })

  test('I should not be able to validate a cancelled countermark', async ({ page }) => {
    await loginAndGoToPage(page, body.user.email, "/guichet")

    await test.step(`I add this countermark "${tokenCanceled}"`, async () => {
      await page.getByLabel('Contremarque').fill(tokenCanceled)
    })

    await test.step('the countermark is rejected as canceled', async () => {
      await expect(page.getByText('Cette réservation a été annulée')).toBeVisible()
      await expect(page.getByRole('button', { name: 'Valider la contremarque' })).toBeDisabled()
    })
  })

  test('I should not be able to validate a reimbursed countermark', async ({ page }) => {
    await loginAndGoToPage(page, body.user.email, "/guichet")

    await test.step(`I add this countermark "${tokenReimbursed}"`, async () => {
      await page.getByLabel('Contremarque').fill(tokenReimbursed)
    })

    await test.step('the countermark is rejected as reimbursed', async () => {
      await expect(page.getByText('Cette réservation a été remboursée')).toBeVisible()
      await expect(page.getByRole('button', { name: 'Valider la contremarque' })).toBeDisabled()
    })
  })
})
