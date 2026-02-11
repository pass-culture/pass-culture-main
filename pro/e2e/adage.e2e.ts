import { expect, test } from './fixtures/adage'
import { expectSuccessSnackbar } from './helpers/assertions'
import {
  isAdageAddFavoriteResponse,
  isAdageRemoveFavoriteResponse,
} from './helpers/requests'

test.describe('ADAGE discovery', () => {
  test.beforeEach(async ({ adagePage: page, adageSession }) => {
    await page.route('**/queries?x-algolia-agent=*', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
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
                    description:
                      'a passionate description of collectiveoffer 98',
                  },
                  offerer: {
                    name: 'eac_pending_bank_informations',
                  },
                  venue: {
                    academy: 'Paris',
                    departmentCode: '75',
                    id: 881,
                    name: 'reimbursementPoint eac_pending_bank_informations',
                    publicName:
                      'reimbursementPoint eac_pending_bank_informations',
                    adageId: '789456',
                  },
                  _geoloc: {
                    lat: 48.87004,
                    lng: 2.3785,
                  },
                  isTemplate: true,
                  formats: ['Projection audiovisuelle'],
                  objectID: `T-${adageSession.data.offerId}`,
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
                        value:
                          'reimbursementPoint eac_pending_bank_informations',
                        matchLevel: 'none',
                        matchedWords: [],
                      },
                      publicName: {
                        value:
                          'reimbursementPoint eac_pending_bank_informations',
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
                    publicName:
                      'reimbursementPoint eac_pending_bank_informations',
                  },
                  isTemplate: true,
                  objectID: `T-${adageSession.data.offerId}`,
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
        }),
      })
    })
  })

  test('It should put an offer in favorite', async ({
    adagePage: page,
    adageSession,
  }) => {
    await page.goto(`/adage-iframe/recherche?token=${adageSession.token}`)
    await expect(page.getByTestId('offer-listitem')).toBeVisible()

    await page.getByText(`${adageSession.data.offerName}`).click()
    await Promise.all([
      page.waitForResponse(isAdageAddFavoriteResponse),
      page.getByTestId('favorite-inactive').click(),
    ])
    await expectSuccessSnackbar(page, 'Ajouté à vos favoris')

    await page.getByRole('link', { name: 'Mes Favoris' }).click()
    await expect(
      page.getByRole('heading', { name: `${adageSession.data.offerName}` })
    ).toBeVisible()

    await Promise.all([
      page.waitForResponse(isAdageRemoveFavoriteResponse),
      page.getByTestId('favorite-active').click(),
    ])
    await expectSuccessSnackbar(page, 'Supprimé de vos favoris')
  })

  // À remplacer par un test unitaire/d'intégration ?
  test('It should redirect to adage discovery', async ({
    adagePage: page,
    adageSession,
  }) => {
    await page.goto(`/adage-iframe?token=${adageSession.token}`)
    await expect(
      page.getByRole('link', { name: 'Découvrir (Onglet actif)' }).first()
    ).toHaveAttribute('aria-current', 'page')

    await expect(
      page.locator('[class^=_discovery-banner]').first()
    ).toContainText(/Découvrez la part collective du pass Culture/)
  })

  test('It should redirect to search page with filtered venue on click in venue card', async ({
    adagePage: page,
    adageSession,
  }) => {
    await page.goto(`/adage-iframe?token=${adageSession.token}`)
    await page.getByText(adageSession.data.venueName).click()

    await expect(
      page.getByRole('link', { name: 'Rechercher (Onglet actif)' })
    ).toHaveAttribute('aria-current', 'page')
    await expect(
      page.getByText(`Lieu : ${adageSession.data.venueName}`)
    ).toBeVisible()
  })

  test('It should redirect to search page with filtered domain on click in domain card', async ({
    adagePage: page,
    adageSession,
  }) => {
    await page.goto(`/adage-iframe?token=${adageSession.token}`)
    await page.getByText('Danse').first().click()

    await expect(
      page.getByRole('link', { name: 'Rechercher (Onglet actif)' })
    ).toHaveAttribute('aria-current', 'page')

    await expect(
      page.getByRole('link', { name: 'Rechercher (Onglet actif)' })
    ).toHaveAttribute('aria-current', 'page')
    await expect(page.getByRole('button', { name: /Danse/ })).toBeVisible()
  })

  test('It should not keep filters after page change', async ({
    adagePage: page,
    adageSession,
  }) => {
    await page.goto(`/adage-iframe?token=${adageSession.token}`)
    await page.getByText(adageSession.data.venueName).click()

    await expect(
      page.getByText(`Lieu : ${adageSession.data.venueName}`)
    ).toBeVisible()

    await page.getByRole('link', { name: 'Découvrir' }).click()
    await page.getByRole('link', { name: 'Rechercher' }).click()

    await expect(
      page.getByText(`Lieu : ${adageSession.data.venueName}`)
    ).not.toBeVisible()
  })

  test('It should save view type in search page', async ({
    adagePage: page,
    adageSession,
  }) => {
    await page.goto(`/adage-iframe/recherche?token=${adageSession.token}`)
    await expect(page.getByTestId('offer-listitem')).toBeVisible()
    await expect(page.getByTestId('offer-description')).toBeVisible()

    await page.getByTestId('toggle-button').click()
    await expect(page.getByTestId('offer-description')).not.toBeVisible()

    await page.getByText('Mes Favoris').click()
    await expect(
      page.getByText(/Vous n’avez pas d’offres en favoris/)
    ).toBeVisible()

    await page.getByText('Rechercher').click()
    await expect(page.getByTestId('offer-listitem')).toBeVisible()
    await expect(page.getByTestId('offer-description')).not.toBeVisible()
  })

  test('It should save filter when page changing', async ({
    adagePage: page,
    adageSession,
  }) => {
    await page.goto(`/adage-iframe?token=${adageSession.token}`)
    await page.getByText(adageSession.data.venueName).click()

    await expect(
      page.getByText(`Lieu : ${adageSession.data.venueName}`)
    ).toBeVisible()
    await page.getByRole('button', { name: 'Domaine artistique' }).click()
    await page.getByLabel('Danse').click()
    await page.getByRole('button', { name: 'Rechercher' }).first().click()

    await page.getByRole('button', { name: 'Format' }).click()
    await page.getByLabel('Concert').click()
    await page.getByRole('button', { name: 'Rechercher' }).first().click()

    await page.getByText('Mes Favoris').click()
    await expect(
      page.getByText(/Vous n’avez pas d’offres en favoris/)
    ).toBeVisible()

    await page.getByText('Rechercher').click()

    await page.getByRole('button', { name: 'Format (1)' }).click()
    await expect(
      page.getByRole('checkbox', { name: 'Concert' }).first()
    ).toBeChecked()

    await page.getByRole('button', { name: 'Domaine artistique (1)' }).click()
    await expect(page.getByRole('checkbox', { name: 'Danse' })).toBeChecked()
    await expect(
      page.getByText(`Lieu : ${adageSession.data.venueName}`)
    ).toBeVisible()
  })

  test('It should save page when navigating the iframe', async ({
    adagePage: page,
    adageSession,
  }) => {
    await page.goto(`/adage-iframe/recherche?token=${adageSession.token}`)
    await page.getByRole('button', { name: /page suivante/ }).click()
    await expect(
      page.getByRole('button', { name: /Page 2 sur 19/ })
    ).toBeVisible()

    await page.getByText('Mes Favoris').click()
    await expect(
      page.getByText(/Vous n’avez pas d’offres en favoris/)
    ).toBeVisible()

    await page.getByText('Rechercher').click()
    await expect(
      page.getByRole('button', { name: /Page 2 sur 19/ })
    ).toBeVisible()
  })
})
