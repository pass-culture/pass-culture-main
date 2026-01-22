import { expect, test } from './fixtures/searchCollectiveTemplateOffer'
import { checkAccessibility } from './helpers/accessibility'

test.describe('Search collective template offers (Optimized)', () => {
  test('I can search by name and see the expected result', async ({
    page,
    templateOffersData,
  }) => {
    await checkAccessibility(page)

    const collectiveOffersResponse = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/offers-template') &&
        response.request().method() === 'GET'
    )

    await page
      .getByLabel('Nom de l’offre')
      .fill(templateOffersData.offerPublished.name)
    await page.getByRole('button', { name: 'Rechercher' }).click()

    expect((await collectiveOffersResponse).status()).toBe(200)

    const row = page
      .locator('tbody')
      .locator('tr[data-testid="table-row"]')
      .filter({ hasText: templateOffersData.offerPublished.name })
      .first()

    await expect(row).toBeVisible()
    await expect(row).toContainText(templateOffersData.offerPublished.name)
    await expect(row).toContainText('publiée')
  })

  test('I can search by location and see the expected result', async ({
    page,
    templateOffersData,
  }) => {
    const collectiveOffersResponse = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/offers-template') &&
        response.request().method() === 'GET'
    )

    await page.getByRole('button', { name: 'Filtrer' }).click()
    await page
      .getByLabel('Localisation')
      .selectOption('En établissement scolaire')
    await page.getByRole('button', { name: 'Rechercher' }).click()

    expect((await collectiveOffersResponse).status()).toBe(200)

    const row = page
      .locator('tbody')
      .locator('tr[data-testid="table-row"]')
      .filter({ hasText: templateOffersData.offerArchived.name })
      .first()

    await expect(row).toBeVisible()
    await expect(row).toContainText(templateOffersData.offerArchived.name)
    await expect(row).toContainText('archivée')
  })

  test('I can search by format "Atelier de pratique" and see the expected result', async ({
    page,
    templateOffersData,
  }) => {
    const collectiveOffersResponse = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/offers-template') &&
        response.request().method() === 'GET'
    )

    await page.getByRole('button', { name: 'Filtrer' }).click()
    await page.getByLabel('Format').selectOption('Atelier de pratique')
    await page.getByRole('button', { name: 'Rechercher' }).click()

    expect((await collectiveOffersResponse).status()).toBe(200)

    const row = page
      .locator('tbody')
      .locator('tr[data-testid="table-row"]')
      .filter({ hasText: templateOffersData.offerPublished.name })
      .first()

    await expect(row).toBeVisible()
    await expect(row).toContainText(templateOffersData.offerPublished.name)
    await expect(row).toContainText('publiée')
  })

  test('I can search by format "Représentation" and see the expected result', async ({
    page,
    templateOffersData,
  }) => {
    const collectiveOffersResponse = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/offers-template') &&
        response.request().method() === 'GET'
    )

    await page.getByRole('button', { name: 'Filtrer' }).click()
    await page.getByLabel('Format').selectOption('Représentation')
    await page.getByRole('button', { name: 'Rechercher' }).click()

    expect((await collectiveOffersResponse).status()).toBe(200)

    const tbody = page.locator('tbody')
    await expect(tbody).toContainText(templateOffersData.offerDraft.name)
    await expect(tbody).toContainText('brouillon')
    await expect(tbody).toContainText(templateOffersData.offerUnderReview.name)
    await expect(tbody).toContainText('instruction')
    await expect(tbody).toContainText(templateOffersData.offerRejected.name)
    await expect(tbody).toContainText('non conforme')
  })

  test('I can search by status "Published" and see the expected result', async ({
    page,
    templateOffersData,
  }) => {
    const collectiveOffersResponse = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/offers-template') &&
        response.request().method() === 'GET'
    )

    await page.getByRole('button', { name: 'Filtrer' }).click()
    await page.getByRole('button', { name: 'Statut' }).click()
    await page.getByText('Publiée sur ADAGE').click()
    await page.getByRole('button', { name: 'Rechercher' }).click()

    expect((await collectiveOffersResponse).status()).toBe(200)

    const row = page
      .locator('tbody')
      .locator('tr[data-testid="table-row"]')
      .filter({ hasText: templateOffersData.offerPublished.name })
      .first()

    await expect(row).toBeVisible()
    await expect(row).toContainText(templateOffersData.offerPublished.name)
    await expect(row).toContainText('publiée')
  })

  test('I can search by status "Draft" and see the expected result', async ({
    page,
    templateOffersData,
  }) => {
    const collectiveOffersResponse = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/offers-template') &&
        response.request().method() === 'GET'
    )

    await page.getByRole('button', { name: 'Filtrer' }).click()
    await page.getByRole('button', { name: 'Statut' }).click()

    const panelScrollable = page.getByTestId('panel-scrollable')
    await panelScrollable.getByText('Brouillon').click()

    await page.getByRole('button', { name: 'Rechercher' }).click()

    const response = await collectiveOffersResponse
    expect(response.status()).toBe(200)

    const row = page
      .locator('tbody')
      .locator('tr[data-testid="table-row"]')
      .filter({ hasText: templateOffersData.offerDraft.name })
      .first()

    await expect(row).toBeVisible()
    await expect(row).toContainText(templateOffersData.offerDraft.name)
    await expect(row).toContainText('brouillon')
  })

  test('I can combine several filters and reset them', async ({
    page,
    templateOffersData,
  }) => {
    const collectiveOffersResponse = page.waitForResponse(
      (response) =>
        response.url().includes('/collective/offers-template') &&
        response.request().method() === 'GET'
    )

    await page.getByRole('button', { name: 'Filtrer' }).click()
    await page
      .getByLabel('Localisation')
      .selectOption('En établissement scolaire')
    await page.getByRole('button', { name: 'Statut' }).click()

    const panelScrollable = page.getByTestId('panel-scrollable')
    await panelScrollable.getByText('En instruction').click()
    await panelScrollable.getByText('Non conforme').click()

    await page.getByRole('button', { name: 'Rechercher' }).click()

    expect((await collectiveOffersResponse).status()).toBe(200)

    await expect(
      page.getByText('Aucune offre trouvée pour votre recherche')
    ).toBeVisible()

    await page
      .getByRole('button', { name: 'Réinitialiser les filtres' })
      .click()

    await page.getByRole('button', { name: 'Statut' }).click()

    const statusPanel = page.getByTestId('panel-scrollable')
    await expect(statusPanel.getByText('En instruction')).not.toBeChecked()
    await expect(statusPanel.getByText('Non conforme')).not.toBeChecked()

    await expect(
      page.getByRole('combobox', { name: /Localisation/ })
    ).toHaveValue('all')
    await expect(page.getByRole('combobox', { name: /Format/ })).toHaveValue(
      'all'
    )

    await page.getByLabel('Nom de l’offre').clear()
    await page.getByRole('button', { name: 'Rechercher' }).click()

    const tbody = page.locator('tbody')
    await expect(tbody).toContainText(templateOffersData.offerPublished.name)
    await expect(tbody).toContainText(templateOffersData.offerDraft.name)
    await expect(tbody).toContainText(templateOffersData.offerArchived.name)
    await expect(tbody).toContainText(templateOffersData.offerUnderReview.name)
    await expect(tbody).toContainText(templateOffersData.offerRejected.name)
  })
})
