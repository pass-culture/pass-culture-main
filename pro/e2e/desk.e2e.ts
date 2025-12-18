import { addDays, format } from 'date-fns'

import { expect, test } from './fixtures/test'

test.describe('Desk (Guichet)', () => {
  test.describe.configure({ mode: 'serial' })

  test('should display help information on desk page', async ({
    authenticatedPage: page,
  }) => {
    await expect(
      page.getByText(
        /N.oubliez pas de vérifier l.identité du bénéficiaire avant de valider la contremarque/
      )
    ).toBeVisible()

    await expect(
      page.getByText(
        /Les pièces d.identité doivent impérativement être présentées physiquement/
      )
    ).toBeVisible()

    const cguLink = page.getByRole('link', {
      name: 'Modalités de retrait et CGU',
    })
    await expect(cguLink).toBeVisible()

    const href = await cguLink.getAttribute('href')
    expect(href).toContain('aide.passculture.app')
    expect(href).toContain('Acteurs-Culturels-Modalit')
  })

  test('should validate a valid countermark', async ({
    authenticatedPage: page,
    deskData,
    checkAccessibility,
  }) => {
    const tokenInput = page.getByLabel('Contremarque')
    await tokenInput.fill(deskData.tokenConfirmed)

    await expect(
      page.getByText(/Coupon vérifié, cliquez sur .Valider. pour enregistrer/)
    ).toBeVisible()

    await page.getByRole('button', { name: 'Valider la contremarque' }).click()

    await expect(page.getByText('Contremarque validée !')).toBeVisible()

    const a11yResults = await checkAccessibility()
    expect(a11yResults.violations).toHaveLength(0)
  })

  test('should decline a non-valid countermark', async ({
    authenticatedPage: page,
  }) => {
    const tokenInput = page.getByLabel('Contremarque')
    await tokenInput.fill('XXXXXX')

    await expect(page.getByTestId('desk-message')).toContainText(
      /La contremarque n.existe pas/
    )

    await expect(
      page.getByRole('button', { name: 'Valider la contremarque' })
    ).toBeDisabled()
  })

  test('should decline an event countermark more than 48h before', async ({
    authenticatedPage: page,
    deskData,
  }) => {
    const tokenInput = page.getByLabel('Contremarque')
    await tokenInput.fill(deskData.tokenTooSoon)

    const expectedDate = format(addDays(new Date(), 2), 'dd/MM/yyyy')

    const deskMessage = page.getByTestId('desk-message')
    await expect(deskMessage).toContainText(
      `Vous pourrez valider cette contremarque à partir du ${expectedDate}`
    )
    await expect(deskMessage).toContainText(
      /une fois le délai d.annulation passé/
    )

    await expect(
      page.getByRole('button', { name: 'Valider la contremarque' })
    ).toBeDisabled()
  })

  test('should invalidate an already used countermark', async ({
    authenticatedPage: page,
    deskData,
  }) => {
    const tokenInput = page.getByLabel('Contremarque')
    await tokenInput.fill(deskData.tokenUsed)

    await expect(
      page.getByText(/Cette contremarque a été validée/)
    ).toBeVisible()

    await page
      .getByRole('button', { name: 'Invalider la contremarque' })
      .click()
    await page.getByRole('button', { name: 'Continuer' }).click()

    await expect(page.getByText('Contremarque invalidée !')).toBeVisible()
  })

  test('should not validate another pro countermark', async ({
    authenticatedPage: page,
    deskData,
  }) => {
    const tokenInput = page.getByLabel('Contremarque')
    await tokenInput.fill(deskData.tokenOther)

    await expect(
      page.getByRole('button', { name: 'Valider la contremarque' })
    ).toBeDisabled()

    await expect(page.getByText(/La contremarque n.existe pas/)).toBeVisible()
  })

  test('should not validate a cancelled countermark', async ({
    authenticatedPage: page,
    deskData,
  }) => {
    const tokenInput = page.getByLabel('Contremarque')
    await tokenInput.fill(deskData.tokenCanceled)

    await expect(
      page.getByRole('button', { name: 'Valider la contremarque' })
    ).toBeDisabled()

    await expect(
      page.getByText('Cette réservation a été annulée')
    ).toBeVisible()
  })

  test('should not validate a reimbursed countermark', async ({
    authenticatedPage: page,
    deskData,
  }) => {
    const tokenInput = page.getByLabel('Contremarque')
    await tokenInput.fill(deskData.tokenReimbursed)

    await expect(
      page.getByRole('button', { name: 'Valider la contremarque' })
    ).toBeDisabled()

    await expect(
      page.getByText('Cette réservation a été remboursée')
    ).toBeVisible()
  })
})
