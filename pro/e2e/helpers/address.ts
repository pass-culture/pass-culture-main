import type { Expect, Locator, Page } from '@playwright/test'

export const MOCKED_BACK_ADDRESS_LABEL = '3 Rue de Valois 75001 Paris'
export const MOCKED_BACK_ADDRESS_STREET = '3 RUE DE VALOIS'

export function mockAddressSearch(page: Page) {
  return page.route('**/geocodage/search/?limit=5&q=*', (route) => {
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        type: 'FeatureCollection',
        version: 'draft',
        features: [
          {
            type: 'Feature',
            geometry: {
              type: 'Point',
              coordinates: [2.3056966, 48.8716934],
            },
            properties: {
              label: MOCKED_BACK_ADDRESS_LABEL,
              score: 0.97351,
              housenumber: '89',
              id: '75108_5194_00089',
              name: MOCKED_BACK_ADDRESS_STREET,
              postcode: '75008',
              citycode: '75108',
              x: 649261.94,
              y: 6863742.69,
              city: 'Paris',
              district: 'Paris 8e Arrondissement',
              context: '75, Paris, Île-de-France',
              type: 'housenumber',
              importance: 0.70861,
              street: MOCKED_BACK_ADDRESS_STREET,
            },
          },
        ],
        attribution: 'BAN',
        licence: 'ETALAB-2.0',
        query: MOCKED_BACK_ADDRESS_LABEL,
        limit: 5,
      }),
    })
  })
}

export async function autoCompleteAddress(
  page: Page,
  address: string = MOCKED_BACK_ADDRESS_LABEL
) {
  await page.getByLabel(/Adresse postale/).fill(address)

  await page
    .getByTestId('list')
    .filter({ has: page.getByText(address) })
    .click()
}

async function fillAndCheckValidity(
  locator: Locator,
  value: string,
  expect: Expect
) {
  await locator.fill(value)
  await locator.blur()
  await expect(locator).toHaveAttribute('aria-invalid', 'false')
}

export async function fillCustomAddress(page: Page, expect: Expect) {
  await page
    .getByRole('button', { name: 'Vous ne trouvez pas votre adresse ?' })
    .click()
  await fillAndCheckValidity(
    page.getByLabel('Intitulé de la localisation'),
    'Libellé de mon adresse custom',
    expect
  )
  await fillAndCheckValidity(
    page.getByLabel(/Adresse postale/).last(),
    'Place de la gare',
    expect
  )
  await fillAndCheckValidity(page.getByLabel(/Code postal/), '123123', expect)
  await fillAndCheckValidity(page.getByLabel(/Ville/), 'Y', expect)
  await fillAndCheckValidity(
    page.getByLabel(/Coordonnées GPS/),
    '48.853320, 2.348979',
    expect
  )

  await expect(
    page.getByText('Contrôlez la précision de vos coordonnées GPS.')
  ).toBeVisible()
}
