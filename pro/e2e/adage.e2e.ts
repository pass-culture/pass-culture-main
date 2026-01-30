import { expect, test } from '@playwright/test'

interface SandboxResponse {
  offerId: number
  offerName: string
  venueName: string
}

test.describe('ADAGE discovery', () => {
  let offerId: number
  let adageToken: string
  let offerName: string
  let venueName: string

  const mockAlgoliaResponse = (offerId: number) => ({
    results: [
      {
        hits: [
          {
            offer: {
              dateCreated: 1726907257.840899,
              name: 'offer 280 pour eac_pending_bank_informations template request',
              students: ['Lycée - Seconde'],
              domains: [10],
              interventionArea: ['2A', '2B'],
              locationType: 'TO_BE_DEFINED',
              description: 'a passionate description of collectiveoffer 98',
            },
            offerer: {
              name: 'eac_pending_bank_informations',
            },
            venue: {
              academy: 'Paris',
              departmentCode: '75',
              id: 881,
              name: 'reimbursementPoint eac_pending_bank_informations',
              publicName: 'reimbursementPoint eac_pending_bank_informations',
              adageId: '789456',
            },
            _geoloc: {
              lat: 48.87004,
              lng: 2.3785,
            },
            isTemplate: true,
            formats: ['Projection audiovisuelle'],
            objectID: `T-${offerId}`,
            _highlightResult: {
              offer: {
                name: {
                  value:
                    'offer 280 pour eac_pending_bank_informations template request',
                  matchLevel: 'none',
                  matchedWords: [],
                },
                description: {
                  value: 'a passionate description of collectiveoffer 98',
                  matchLevel: 'none',
                  matchedWords: [],
                },
              },
              offerer: {
                name: {
                  value: 'eac_pending_bank_informations',
                  matchLevel: 'none',
                  matchedWords: [],
                },
              },
              venue: {
                name: {
                  value: 'reimbursementPoint eac_pending_bank_informations',
                  matchLevel: 'none',
                  matchedWords: [],
                },
                publicName: {
                  value: 'reimbursementPoint eac_pending_bank_informations',
                  matchLevel: 'none',
                  matchedWords: [],
                },
              },
            },
          },
        ],
        nbHits: 1,
        page: 0,
        nbPages: 1,
        hitsPerPage: 20,
        exhaustiveNbHits: true,
        exhaustiveTypo: true,
        exhaustive: {
          nbHits: true,
          typo: true,
        },
        query: '',
        params: '',
        index: 'testing-collective-offers',
        renderingContent: {},
        processingTimeMS: 2,
        processingTimingsMS: {
          _request: {
            roundTrip: 13,
          },
          afterFetch: {
            format: {
              total: 1,
            },
          },
          getIdx: {
            load: {
              total: 1,
            },
            total: 2,
          },
          total: 2,
        },
        serverTimeMS: 4,
      },
      {
        hits: [
          {
            offer: {
              name: 'offer 280 pour eac_pending_bank_informations template request',
              interventionArea: ['2A', '2B'],
            },
            venue: {
              name: 'reimbursementPoint eac_pending_bank_informations',
              publicName: 'reimbursementPoint eac_pending_bank_informations',
            },
            isTemplate: true,
            objectID: `T-${offerId}`,
          },
        ],
        nbHits: 1,
        page: 0,
        nbPages: 19,
        hitsPerPage: 8,
        exhaustiveNbHits: true,
        exhaustiveTypo: true,
        exhaustive: {
          nbHits: true,
          typo: true,
        },
        query: '',
        params:
          'aroundLatLng=48.8566%2C%202.3522&aroundRadius=30000000&attributesToHighlight=%5B%5D&attributesToRetrieve=%5B%22objectID%22%2C%22offer.dates%22%2C%22offer.name%22%2C%22offer.thumbUrl%22%2C%22venue.name%22%2C%22venue.publicName%22%2C%22isTemplate%22%2C%22offer.interventionArea%22%5D&clickAnalytics=true&distinct=false&filters=offer.locationType%3AADDRESS%3Cscore%3D3%3E%20OR%20offer.locationType%3ASCHOOL%3Cscore%3D2%3E%20OR%20offer.locationType%3ATO_BE_DEFINED%3Cscore%3D1%3E&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=8&page=0&query=',
        index: 'testing-collective-offers',
        queryID: '324dafe3bdf5ec1e8bfeb03f89044fc0',
        renderingContent: {},
        processingTimeMS: 1,
        processingTimingsMS: {
          _request: {
            roundTrip: 13,
          },
        },
        serverTimeMS: 5,
      },
    ],
  })

  test.beforeEach(async ({ page, request }) => {
    // Get fake adage token
    const tokenResponse = await request.get(
      'http://localhost:5001/adage-iframe/testing/token'
    )
    const tokenData = await tokenResponse.json()
    adageToken = tokenData.token

    // Call sandbox to create environment
    const sandboxResponse = await request.get(
      'http://localhost:5001/sandboxes/pro/create_adage_environment'
    )
    const sandboxData: SandboxResponse = await sandboxResponse.json()
    offerId = sandboxData.offerId
    offerName = sandboxData.offerName
    venueName = sandboxData.venueName

    // Mock Algolia search
    await page.route(
      'https://testinghxxtdue7h0-dsn.algolia.net/**',
      async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockAlgoliaResponse(offerId)),
        })
      }
    )
  })

  test('It should put an offer in favorite', async ({ page }) => {
    const authenticatePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/adage-iframe/authenticate') &&
        response.status() === 200
    )
    const catalogViewPromise = page.waitForResponse(
      (response) =>
        response.url().includes('/adage-iframe/logs/catalog-view') &&
        response.status() === 204
    )

    await page.goto(`/adage-iframe/recherche?token=${adageToken}`)

    await authenticatePromise
    await catalogViewPromise

    // Wait for spinner to disappear
    await expect(page.getByTestId('spinner')).toHaveCount(0)
    await expect(page.getByTestId('offer-listitem')).toContainText(offerName)

    // Add first offer to favorites
    await test.step('I add first offer to favorites', async () => {
      await page.getByText(offerName).click()
      await page.getByTestId('favorite-inactive').click()

      const favResponse = await page.waitForResponse(
        (response) =>
          response.url().includes('/adage-iframe/logs/fav-offer/') &&
          response.status() === 204,
        { timeout: 30000 }
      )
      expect(favResponse.status()).toBe(204)

      await expect(
        page.getByTestId('global-snack-bar-success-0')
      ).toContainText('Ajouté à vos favoris')
    })

    // Check offer is in favorites
    await test.step('the first offer should be added to favorites', async () => {
      await page.getByText('Mes Favoris').click()
      await expect(page.getByText(offerName)).toBeVisible()
    })

    // Remove from favorites
    await test.step('we can remove it from favorites', async () => {
      await page.getByTestId('favorite-active').click()

      const deleteResponse = await page.waitForResponse(
        (response) =>
          response.url().includes('/adage-iframe/collective/template/') &&
          response.url().includes('/favorites') &&
          response.request().method() === 'DELETE' &&
          response.status() === 204
      )
      expect(deleteResponse.status()).toBe(204)

      await expect(
        page.getByTestId('global-snack-bar-success-1')
      ).toContainText('Supprimé de vos favoris')
    })
  })

  test('It should redirect to adage discovery', async ({ page }) => {
    const authenticatePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/adage-iframe/authenticate') &&
        response.status() === 200
    )

    await page.goto(`/adage-iframe?token=${adageToken}`)
    await authenticatePromise

    await test.step('the iframe should be displayed correctly', async () => {
      await expect(page).toHaveURL(/\/decouverte/)
      const discoverLink = page
        .getByRole('link', { name: 'Découvrir (Onglet actif)' })
        .first()
      await expect(discoverLink).toHaveAttribute('aria-current', 'page')
    })

    await test.step('the banner is displayed', async () => {
      const banner = page.locator('[class^=_discovery-banner]')
      await expect(banner).toContainText(
        'Découvrez la part collective du pass Culture'
      )
    })
  })

  test('It should redirect to a page dedicated to the offer with an active header on the discovery tab', async ({
    page,
  }) => {
    const authenticatePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/adage-iframe/authenticate') &&
        response.status() === 200
    )

    await page.goto(`/adage-iframe?token=${adageToken}`)
    await authenticatePromise

    await test.step('I click on an offer', async () => {
      await page.getByText(offerName).click()
    })

    await test.step('the iframe should be displayed correctly', async () => {
      await expect(page).toHaveURL(/\/decouverte/)
      const discoverLink = page
        .getByRole('link', { name: 'Découvrir (Onglet actif)' })
        .first()
      await expect(discoverLink).toHaveAttribute('aria-current', 'page')
    })
  })

  test('It should redirect to search page with filtered venue on click in venue card', async ({
    page,
  }) => {
    const authenticatePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/adage-iframe/authenticate') &&
        response.status() === 200
    )

    await page.goto(`/adage-iframe?token=${adageToken}`)
    await authenticatePromise

    await test.step('I click on venue', async () => {
      await page.getByText(venueName).click()
    })

    await test.step('the iframe search page should be displayed correctly', async () => {
      await expect(page).toHaveURL(/\/recherche/)
      const searchLink = page.getByRole('link', {
        name: 'Rechercher (Onglet actif)',
      })
      await expect(searchLink).toHaveAttribute('aria-current', 'page')
    })

    await test.step('Venue filter should be there', async () => {
      await expect(page.getByText(`Lieu : ${venueName}`)).toBeVisible()
    })
  })

  test('It should redirect to search page with filtered domain on click in domain card', async ({
    page,
  }) => {
    const authenticatePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/adage-iframe/authenticate') &&
        response.status() === 200
    )

    await page.goto(`/adage-iframe?token=${adageToken}`)
    await authenticatePromise

    await test.step('I select first card domain', async () => {
      await page.getByText('Danse').first().click()
    })

    await test.step('the iframe search page should be displayed correctly', async () => {
      await expect(page).toHaveURL(/\/recherche/)
      const searchLink = page.getByRole('link', {
        name: 'Rechercher (Onglet actif)',
      })
      await expect(searchLink).toHaveAttribute('aria-current', 'page')
    })

    await test.step('the "Danse" button should be displayed', async () => {
      await expect(
        page.locator('button').filter({ hasText: 'Danse' })
      ).toBeVisible()
    })
  })

  test('It should not keep filters after page change', async ({ page }) => {
    const authenticatePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/adage-iframe/authenticate') &&
        response.status() === 200
    )

    await page.goto(`/adage-iframe?token=${adageToken}`)
    await authenticatePromise

    await test.step('I click on venue', async () => {
      await page.getByText(venueName).click()
    })

    await test.step('the iframe search page should be displayed correctly', async () => {
      await expect(page).toHaveURL(/\/recherche/)
      const searchLink = page.getByRole('link', {
        name: 'Rechercher (Onglet actif)',
      })
      await expect(searchLink).toHaveAttribute('aria-current', 'page')
    })

    await test.step('I go back to search page', async () => {
      await expect(page.getByText(`Lieu : ${venueName}`)).toBeVisible()
      await page.getByRole('link', { name: 'Découvrir' }).click()
      await page.getByRole('link', { name: 'Rechercher' }).click()
    })

    await test.step('The filter has disappear', async () => {
      await expect(page.getByText(`Lieu : ${venueName}`)).not.toBeVisible()
    })
  })

  test('It should not keep filter venue after page change', async ({
    page,
  }) => {
    const authenticatePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/adage-iframe/authenticate') &&
        response.status() === 200
    )

    await page.goto(`/adage-iframe?token=${adageToken}`)
    await authenticatePromise

    await test.step('I click on venue', async () => {
      await page.getByText(venueName).click()
    })

    await test.step('the iframe search page should be displayed correctly', async () => {
      await expect(page).toHaveURL(/\/recherche/)
      const searchLink = page.getByRole('link', {
        name: 'Rechercher (Onglet actif)',
      })
      await expect(searchLink).toHaveAttribute('aria-current', 'page')
    })

    await test.step('I go back to search page', async () => {
      await expect(page.getByText(`Lieu : ${venueName}`)).toBeVisible()
      await page.getByRole('link', { name: 'Découvrir' }).click()
      await page.getByRole('link', { name: 'Rechercher' }).click()
    })

    await test.step('The filter has disappear', async () => {
      await expect(page.getByText(`Lieu : ${venueName}`)).not.toBeVisible()
    })
  })

  test('It should save view type in search page', async ({ page }) => {
    const authenticatePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/adage-iframe/authenticate') &&
        response.status() === 200
    )
    const catalogViewPromise = page.waitForResponse(
      (response) =>
        response.url().includes('/adage-iframe/logs/catalog-view') &&
        response.status() === 204
    )

    await page.goto(`/adage-iframe/recherche?token=${adageToken}`)

    await authenticatePromise
    await catalogViewPromise

    await test.step('offer descriptions are displayed', async () => {
      await expect(page.getByTestId('offer-listitem').first()).toBeVisible()
      await expect(page.getByTestId('offer-description').first()).toBeVisible()
    })

    await test.step('I chose grid view', async () => {
      await page.getByTestId('toggle-button').click()
    })

    await test.step('offer descriptions are not displayed', async () => {
      await expect(page.getByTestId('offer-listitem').first()).toBeVisible()
      await expect(page.getByTestId('offer-description')).toHaveCount(0)
    })

    await test.step('I put my offer in favorite', async () => {
      await page.getByTestId('favorite-inactive').click()
    })

    await test.step('I go to "Mes Favoris" menu', async () => {
      await page.getByText('Mes Favoris').click()
    })

    await test.step('offer descriptions are displayed', async () => {
      await expect(page.getByTestId('offer-listitem').first()).toBeVisible()
      await expect(page.getByTestId('offer-description').first()).toBeVisible()
    })

    await test.step('I go to "Rechercher" menu', async () => {
      await page.getByText('Rechercher').click()
    })

    await test.step('offer descriptions are not displayed', async () => {
      await expect(page.getByTestId('offer-listitem').first()).toBeVisible()
      await expect(page.getByTestId('offer-description')).toHaveCount(0)
    })
  })

  test('It should save filter when page changing', async ({ page }) => {
    const authenticatePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/adage-iframe/authenticate') &&
        response.status() === 200
    )

    await page.goto(`/adage-iframe?token=${adageToken}`)
    await authenticatePromise

    await test.step('I choose my filters', async () => {
      await page.getByText(venueName).click()

      // Small delay to ensure UI is ready
      await page.waitForTimeout(500)
      await page.getByRole('button', { name: 'Domaine artistique' }).click()
      await page.getByLabel('Danse').click()
      await page.getByRole('button', { name: 'Rechercher' }).first().click()

      await page.getByRole('button', { name: 'Format' }).click()
      await page.getByLabel('Concert').click()
      await page.getByRole('button', { name: 'Rechercher' }).first().click()
    })

    await test.step('I go to "Mes Favoris" menu', async () => {
      await page.getByText('Mes Favoris').click()
    })

    await test.step('I go to "Rechercher" menu', async () => {
      await page.getByText('Rechercher').click()
    })

    await test.step('Filters are selected', async () => {
      await page.getByRole('button', { name: 'Format (1)' }).click()
      await expect(page.getByLabel('Concert')).toBeChecked()

      await page.getByRole('button', { name: 'Domaine artistique (1)' }).click()
      await expect(page.getByLabel('Danse')).toBeChecked()

      await expect(page.getByText(`Lieu : ${venueName}`)).toBeVisible()
    })
  })

  test('It should save page when navigating the iframe', async ({ page }) => {
    const authenticatePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/adage-iframe/authenticate') &&
        response.status() === 200
    )
    const catalogViewPromise = page.waitForResponse(
      (response) =>
        response.url().includes('/adage-iframe/logs/catalog-view') &&
        response.status() === 204
    )

    await page.goto(`/adage-iframe/recherche?token=${adageToken}`)

    await authenticatePromise
    await catalogViewPromise

    await test.step('I go the the next page of searched offers', async () => {
      await page.getByRole('button', { name: /page suivante/ }).click()
      await expect(
        page.getByRole('button', { name: /Page 2 sur 19/ })
      ).toBeVisible()
    })

    await test.step('I go to "Mes Favoris" menu', async () => {
      await page.getByText('Mes Favoris').click()
    })

    await test.step('I go to "Rechercher" menu', async () => {
      await page.getByText('Rechercher').click()
    })

    await test.step('page has not changed', async () => {
      await expect(
        page.getByRole('button', { name: /Page 2 sur 19/ })
      ).toBeVisible()
    })
  })
})
