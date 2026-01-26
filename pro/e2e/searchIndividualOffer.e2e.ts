import { addDays, format } from 'date-fns'

import { expect, test } from './fixtures/searchIndividualOffer'
import { checkAccessibility } from './helpers/accessibility'
import { expectIndividualOffersOrBookingsAreFound } from './helpers/assertions'

test.describe('Search individual offers', () => {
  test('I should be able to search with a name and see expected results', async ({
    authenticatedPage: page,
    individualOffersUserData: userData,
  }) => {
    const { venue, offer1: offerName1 } = userData

    await page.goto('/offres')

    const searchOffersPromise = page.waitForResponse((response) =>
      response.url().includes('/offers?')
    )

    await page
      .getByRole('searchbox', { name: /Nom de l’offre/ })
      .fill(offerName1.name)
    await checkAccessibility(page)
    await page.getByText('Rechercher').click()
    const searchResponse = await searchOffersPromise
    expect(searchResponse.status()).toBe(200)

    const expectedResults = [
      ['', 'Titre', 'Localisation', 'Stocks', 'Status'],
      [
        '',
        offerName1.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
    ]

    await expectIndividualOffersOrBookingsAreFound(page, expectedResults)
  })

  test('I should be able to search with a EAN and see expected results', async ({
    authenticatedPage: page,
    individualOffersUserData: userData,
  }) => {
    const { venue, offer2: offerName2 } = userData
    const ean = '1234567891234'

    await page.goto('/offres')

    const searchOffersPromise = page.waitForResponse((response) =>
      response.url().includes('/offers?')
    )

    await page.getByRole('searchbox', { name: /Nom de l’offre/ }).fill(ean)
    await page.getByText('Rechercher').click()
    const searchResponse = await searchOffersPromise
    expect(searchResponse.status()).toBe(200)

    const expectedResults = [
      ['', 'Titre', 'Localisation', 'Stocks', 'Status'],
      [
        '',
        offerName2.name + ean,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
    ]

    await expectIndividualOffersOrBookingsAreFound(page, expectedResults)
  })

  test('I should be able to search with "Catégorie" filter and see expected results', async ({
    authenticatedPage: page,
    individualOffersUserData: userData,
  }) => {
    const { venue, offer3: offerName3 } = userData

    await page.goto('/offres')

    await page.getByText('Filtrer').click()

    await page
      .getByRole('combobox', { name: /Catégorie/ })
      .selectOption('Instrument de musique')
    await expect(page.getByRole('combobox', { name: /Catégorie/ })).toHaveValue(
      'INSTRUMENT'
    )

    const searchOffersPromise = page.waitForResponse((response) =>
      response.url().includes('/offers?')
    )
    await page.getByText('Rechercher').click()
    const searchResponse = await searchOffersPromise
    expect(searchResponse.status()).toBe(200)

    const expectedResults = [
      ['', 'Titre', 'Localisation', 'Stocks', 'Status'],
      [
        '',
        offerName3.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
    ]

    await expectIndividualOffersOrBookingsAreFound(page, expectedResults)
  })

  test('I should be able to search by offer status and see expected results', async ({
    authenticatedPage: page,
    individualOffersUserData: userData,
  }) => {
    const {
      venue,
      offer1: offerName1,
      offer2: offerName2,
      offer3: offerName3,
      offer4: offerName4,
      offer5: offerName5,
      offer6: offerName6,
    } = userData

    await page.goto('/offres')

    await page.getByText('Filtrer').click()

    await page.getByRole('combobox', { name: 'Statut' }).selectOption('Publiée')
    await expect(page.getByRole('combobox', { name: 'Statut' })).toHaveValue(
      'ACTIVE'
    )

    const searchOffersPromise = page.waitForResponse((response) =>
      response.url().includes('/offers?')
    )
    await page.getByText('Rechercher').click()
    const searchResponse = await searchOffersPromise
    expect(searchResponse.status()).toBe(200)

    const expectedResults = [
      ['', 'Titre', 'Localisation', 'Stocks', 'Status'],
      [
        '',
        offerName6.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName5.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName4.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName3.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName2.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName1.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
    ]

    await expectIndividualOffersOrBookingsAreFound(page, expectedResults)
  })

  test('I should be able to search by date and see expected results', async ({
    authenticatedPage: page,
    individualOffersUserData: userData,
  }) => {
    const { venue, offer4: offerName4 } = userData

    await page.goto('/offres')

    await page.getByText('Filtrer').click()

    const dateSearch = format(addDays(new Date(), 30), 'yyyy-MM-dd')
    await page.getByLabel('Début de la période').fill(dateSearch)
    await page.getByLabel('Fin de la période').fill(dateSearch)

    const searchOffersPromise = page.waitForResponse((response) =>
      response.url().includes('/offers?')
    )
    await page.getByText('Rechercher').click()
    const searchResponse = await searchOffersPromise
    expect(searchResponse.status()).toBe(200)

    const expectedResults = [
      ['', 'Titre', 'Localisation', 'Stocks', 'Status'],
      [
        '',
        offerName4.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
    ]

    await expectIndividualOffersOrBookingsAreFound(page, expectedResults)
  })

  test('I should be able to search by venue and see expected results', async ({
    authenticatedPage: page,
    individualOffersUserData: userData,
  }) => {
    const {
      venue,
      offer1: offerName1,
      offer2: offerName2,
      offer3: offerName3,
      offer4: offerName4,
      offer5: offerName5,
      offer6: offerName6,
      offer7: offerName7,
    } = userData

    await page.goto('/offres')

    await page.getByText('Filtrer').click()
    await page
      .getByRole('combobox', { name: 'Localisation' })
      .selectOption({ index: 1 })

    const searchOffersPromise = page.waitForResponse((response) =>
      response.url().includes('/offers?')
    )
    await page.getByText('Rechercher').click()
    const searchResponse = await searchOffersPromise
    expect(searchResponse.status()).toBe(200)

    const expectedResults = [
      ['', 'Titre', 'Localisation', 'Stocks', 'Status'],
      [
        '',
        offerName7.name,
        `${venue.name} - ${venue.fullAddress}`,
        '0',
        'épuisée',
      ],
      [
        '',
        offerName6.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName5.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName4.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName3.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName2.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName1.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
    ]

    await expectIndividualOffersOrBookingsAreFound(page, expectedResults)
  })

  test('I should be able to search combining several filters and see expected results', async ({
    authenticatedPage: page,
    individualOffersUserData: userData,
  }) => {
    const {
      venue0,
      venue,
      offer0: offerName0,
      offer1: offerName1,
      offer2: offerName2,
      offer3: offerName3,
      offer4: offerName4,
      offer5: offerName5,
      offer6: offerName6,
      offer7: offerName7,
    } = userData

    await page.goto('/offres')

    await page
      .getByRole('searchbox', { name: /Nom de l’offre/ })
      .fill('incroyable')

    let searchOffersPromise = page.waitForResponse((response) =>
      response.url().includes('/offers?')
    )
    await page.getByText('Rechercher').click()
    let searchResponse = await searchOffersPromise
    expect(searchResponse.status()).toBe(200)

    await page.getByText('Filtrer').click()

    await page.getByLabel('Catégorie').selectOption('Livre')

    await page
      .getByLabel('Localisation')
      .selectOption(`${venue.name} - ${venue.fullAddress}`)

    await page.getByRole('combobox', { name: 'Statut' }).selectOption('Publiée')

    searchOffersPromise = page.waitForResponse((response) =>
      response.url().includes('/offers?')
    )
    await page.getByText('Rechercher').click()
    searchResponse = await searchOffersPromise
    expect(searchResponse.status()).toBe(200)

    const expectedResults = [
      ['', 'Titre', 'Localisation', 'Stocks', 'Status'],
      [
        '',
        offerName6.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName5.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
    ]

    await expectIndividualOffersOrBookingsAreFound(page, expectedResults)

    await page.getByText('Réinitialiser les filtres').click()

    await expect(
      page.getByRole('combobox', { name: 'Localisation' })
    ).toHaveValue('all')
    await expect(page.getByRole('combobox', { name: 'Catégorie' })).toHaveValue(
      'all'
    )
    await expect(
      page.getByRole('combobox', { name: 'Mode de création' })
    ).toHaveValue('all')
    await expect(page.getByRole('combobox', { name: 'Statut' })).toHaveValue(
      'all'
    )
    await expect(page.getByLabel('Début de la période')).toHaveValue('')
    await expect(page.getByLabel('Fin de la période')).toHaveValue('')

    await page.getByRole('searchbox', { name: /Nom de l’offre/ }).clear()
    await expect(
      page.getByRole('searchbox', { name: /Nom de l’offre/ })
    ).toHaveValue('')

    await page.getByRole('button', { name: 'Rechercher' }).click()

    const expectedResults2 = [
      ['', 'Titre', 'Localisation', 'Stocks', 'Status'],
      [
        '',
        offerName7.name,
        `${venue.name} - ${venue.fullAddress}`,
        '0',
        'épuisée',
      ],
      [
        '',
        offerName6.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName5.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName4.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName3.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName2.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName1.name,
        `${venue.name} - ${venue.fullAddress}`,
        '1 000',
        'publiée',
      ],
      [
        '',
        offerName0.name,
        `${venue0.name} - ${venue0.fullAddress}`,
        '0',
        'épuisée',
      ],
    ]

    await expectIndividualOffersOrBookingsAreFound(page, expectedResults2)
  })
})
