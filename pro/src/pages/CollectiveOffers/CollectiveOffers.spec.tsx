import { screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router'
import { beforeAll } from 'vitest'

import { api } from '@/apiClient/api'
import {
  CollectiveLocationType,
  CollectiveOfferDisplayedStatus,
  type CollectiveOfferResponseModel,
  type CollectiveOfferStockResponseModel,
  EacFormat,
  type GetOffererAddressResponseModel,
} from '@/apiClient/v1'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { collectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { offererAddressFactory } from '@/commons/utils/factories/offererAddressFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOffers } from './CollectiveOffers'

const LABELS = {
  nameSearchInput: /Nom de l’offre/,
}

const stock: CollectiveOfferStockResponseModel = {
  bookingLimitDatetime: null,
  numberOfTickets: 100,
  price: 10,
}

const offersRecap: CollectiveOfferResponseModel[] = [
  collectiveOfferFactory({ stock }),
]

vi.mock('@/apiClient/api', () => {
  return {
    api: {
      getCollectiveOffers: vi.fn(),
      getOfferer: vi.fn(),
      getOffererAddresses: vi.fn(),
      getVenues: vi.fn(),
      listOfferersNames: vi.fn(),
    },
  }
})

const offererAddress: GetOffererAddressResponseModel[] = [
  offererAddressFactory({
    label: 'Label',
  }),
  offererAddressFactory({
    city: 'New York',
  }),
]

const renderOffers = (
  filters: Partial<CollectiveSearchFiltersParams> = DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  features: string[] = []
) => {
  const route = computeCollectiveOffersUrl(filters)
  const user = sharedCurrentUserFactory()
  renderWithProviders(<CollectiveOffers />, {
    user,
    initialRouterEntries: [route],
    features,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedVenue: makeVenueListItem({ id: 2 }),
      },
      offerer: currentOffererFactory(),
    },
  })
}

const offererId = 1

describe('CollectiveOffers', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue(offersRecap)
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
    })
    vi.spyOn(api, 'getOffererAddresses').mockResolvedValue(offererAddress)
  })

  afterEach(() => {
    window.sessionStorage.clear()
  })

  it('should fetch only bookable offers', async () => {
    renderOffers()

    await waitFor(() => {
      expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
        null,
        offererId,
        null,
        null,
        null,
        null,
        null,
        null,
        null
      )
    })
  })

  describe('filters', () => {
    describe('status filters', () => {
      it('should filter offers given status filter when clicking on "Appliquer"', async () => {
        renderOffers()

        await userEvent.click(
          screen.getByRole('button', {
            name: 'Statut',
          })
        )

        await userEvent.click(screen.getByText('Expirée'))

        await userEvent.click(
          screen.getByRole('button', { name: 'Rechercher' })
        )

        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
            2,
            null,
            offererId,
            [CollectiveOfferDisplayedStatus.EXPIRED],
            null,
            null,
            null,
            null,
            null,
            null
          )
        })
      })

      it('should filter offers given multiple status filter when clicking on "Appliquer"', async () => {
        renderOffers()

        await userEvent.click(
          screen.getByRole('button', {
            name: 'Statut',
          })
        )

        await userEvent.click(screen.getByText('Expirée'))
        await userEvent.click(screen.getByText('Préréservée'))
        await userEvent.click(screen.getByText('Réservée'))

        await userEvent.click(
          screen.getByRole('button', { name: 'Rechercher' })
        )

        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
            2,
            null,
            offererId,
            [
              CollectiveOfferDisplayedStatus.EXPIRED,
              CollectiveOfferDisplayedStatus.PREBOOKED,
              CollectiveOfferDisplayedStatus.BOOKED,
            ],
            null,
            null,
            null,
            null,
            null,
            null
          )
        })
      })

      it('should indicate that no offers match selected filters', async () => {
        vi.spyOn(api, 'getCollectiveOffers')
          .mockResolvedValueOnce(offersRecap)
          .mockResolvedValueOnce([])
        renderOffers()

        await userEvent.click(
          screen.getByRole('button', {
            name: 'Statut',
          })
        )

        await userEvent.click(screen.getByText('Expirée'))

        await userEvent.click(
          screen.getByRole('button', { name: 'Rechercher' })
        )

        await waitFor(() => {
          expect(
            screen.getByText('Aucune offre trouvée pour votre recherche')
          ).toBeInTheDocument()
        })
      })

      it('should not display column titles when no offers are returned', () => {
        vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([])

        renderOffers()

        expect(screen.queryByText('Lieu', { selector: 'th' })).toBeNull()
        expect(screen.queryByText('Stock', { selector: 'th' })).toBeNull()
      })
    })

    describe('location type filters', () => {
      it('should send locationType ADDRESS and offererAddressId when an address is selected', async () => {
        renderOffers()

        const localisationSelect = await screen.findByLabelText('Localisation')

        await waitFor(() => {
          expect(
            within(screen.getByLabelText('Localisation')).getAllByRole('option')
              .length
          ).toBe(5) // all + school + to be defined + 2 addresses
        })

        await userEvent.selectOptions(
          localisationSelect,
          offererAddress[0].id.toString()
        )
        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(localisationSelect).toHaveValue(
            offererAddress[0].id.toString()
          )
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            null,
            offererId,
            null,
            null,
            null,
            null,
            null,
            CollectiveLocationType.ADDRESS,
            offererAddress[0].id
          )
        })
      })

      it('should send locationType TO_BE_DEFINED and offererAddressId null when "À déterminer" is selected', async () => {
        renderOffers()
        const localisationSelect = await screen.findByLabelText('Localisation')
        await userEvent.selectOptions(
          localisationSelect,
          CollectiveLocationType.TO_BE_DEFINED
        )
        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            null,
            offererId,
            null,
            null,
            null,
            null,
            null,
            CollectiveLocationType.TO_BE_DEFINED,
            null
          )
        })
      })

      it('should send locationType SCHOOL and offererAddressId null when "En établissement scolaire" is selected', async () => {
        renderOffers()
        const localisationSelect = await screen.findByLabelText('Localisation')
        await userEvent.selectOptions(
          localisationSelect,
          CollectiveLocationType.SCHOOL
        )
        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            null,
            offererId,
            null,
            null,
            null,
            null,
            null,
            CollectiveLocationType.SCHOOL,
            null
          )
        })
      })

      it('should send locationType and offererAddressId null when "all" is selected', async () => {
        renderOffers()
        const localisationSelect = await screen.findByLabelText('Localisation')
        await userEvent.selectOptions(localisationSelect, 'all')
        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            null,
            offererId,
            null,
            null,
            null,
            null,
            null,
            null,
            null
          )
        })
      })
    })

    describe('on click on search button', () => {
      it('should load offers with written offer name filter', async () => {
        renderOffers()

        const searchInput = screen.getByRole('searchbox', {
          name: LABELS.nameSearchInput,
        })

        await userEvent.type(searchInput, 'Any word')

        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenCalledWith(
            'Any word',
            offererId,
            null,
            null,
            null,
            null,
            null,
            null,
            null
          )
        })
      })

      it('should load offers with selected period beginning date', async () => {
        renderOffers()

        await userEvent.type(
          screen.getByLabelText('Début de la période'),
          '2020-12-25'
        )

        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            null,
            offererId,
            null,
            null,
            '2020-12-25',
            null,
            null,
            null,
            null
          )
        })
      })

      it('should load offers with selected period ending date', async () => {
        renderOffers()
        await userEvent.type(
          screen.getByLabelText('Fin de la période'),
          '2020-12-27'
        )

        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            null,
            offererId,
            null,
            null,
            null,
            '2020-12-27',
            null,
            null,
            null
          )
        })
      })
    })
  })

  describe('page navigation', () => {
    // Necessary because JSDOM doesn't implement the `scrollTo` method
    // (which is used by the `useAccessibleScroll` hook in that component's scope)
    beforeAll(() => {
      Element.prototype.scrollTo = () => {}
      window.scrollTo = () => {}
    })

    it('should display next page when clicking on right arrow', async () => {
      const offers = Array.from({ length: 11 }, () =>
        collectiveOfferFactory({ stock })
      )
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offers)
      renderOffers()

      const nextIcon = await screen.findByRole('button', {
        name: /page suivante/,
      })

      await userEvent.click(nextIcon)

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      expect(screen.getByLabelText(offers[10].name)).toBeInTheDocument()
      expect(screen.queryByText(offers[0].name)).not.toBeInTheDocument()
    })

    it('should display previous page when clicking on left arrow', async () => {
      const offers = Array.from({ length: 11 }, () =>
        collectiveOfferFactory({ stock })
      )
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offers)

      renderOffers()
      const nextIcon = await screen.findByRole('button', {
        name: /page suivante/,
      })

      await userEvent.click(nextIcon)
      const previousIcon = await screen.findByRole('button', {
        name: /page précédente/,
      })

      await userEvent.click(previousIcon)

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      expect(screen.getByLabelText(offers[0].name)).toBeInTheDocument()
      expect(screen.queryByText(offers[10].name)).not.toBeInTheDocument()
    })

    describe('when 101 offers are fetched', () => {
      const offersRecap = Array.from({ length: 101 }, () =>
        collectiveOfferFactory({ stock })
      )

      it('should have max number page of 10', async () => {
        vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)

        renderOffers()

        expect(
          await screen.findByRole('button', { name: /Page 1 sur 10/ })
        ).toBeInTheDocument()
      })

      it('should not display the 101st offer', async () => {
        vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)
        renderOffers()
        const nextIcon = await screen.findByRole('button', {
          name: /page suivante/,
        })

        for (let i = 1; i < 11; i++) {
          await userEvent.click(nextIcon)
        }

        expect(screen.getByLabelText(offersRecap[99].name)).toBeInTheDocument()
        expect(
          screen.queryByText(offersRecap[100].name)
        ).not.toBeInTheDocument()
      })
    })
  })

  describe('should reset filters', () => {
    it('when clicking on "afficher toutes les offres" when no offers are displayed', async () => {
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([])

      const filters = {
        format: EacFormat.ATELIER_DE_PRATIQUE,
      }
      renderOffers(filters)

      await userEvent.click(screen.getByText('Rechercher'))

      await waitFor(() => {
        expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
        expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
          1,
          null,
          offererId,
          null,
          null,
          null,
          null,
          'Atelier de pratique',
          null,
          null
        )
      })

      screen.getByText('Aucune offre trouvée pour votre recherche')

      await userEvent.click(screen.getByText('Afficher toutes les offres'))
      await waitFor(() => {
        expect(api.getCollectiveOffers).toHaveBeenCalledTimes(2)
      })
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        2,
        null,
        offererId,
        null,
        null,
        null,
        null,
        null,
        null,
        null
      )
    })

    it('when clicking on "Réinitialiser les filtres"  - except name', async () => {
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([])

      const name = 'Any word'
      renderOffers({
        name,
        format: EacFormat.ATELIER_DE_PRATIQUE,
      })

      await userEvent.click(screen.getByText('Réinitialiser les filtres'))
      await waitFor(() => {
        expect(api.getCollectiveOffers).toHaveBeenCalledTimes(2)
      })
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        2,
        name,
        offererId,
        null,
        null,
        null,
        null,
        null,
        null,
        null
      )
    })
  })

  it('should show draft offers ', async () => {
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([
      collectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
      }),
      collectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.DRAFT,
      }),
    ])
    renderOffers()

    expect(await screen.findByText('2 offres')).toBeInTheDocument()
  })

  describe('Query Params', () => {
    // We mock `useNavigate()` returned function and not `useNavigate` itself
    const routerUseNavigateReturnMock: router.NavigateFunction = vi.fn()

    const proVenues = [
      makeVenueListItem({
        id: 1,
        name: 'Ma venue',
      }),
      makeVenueListItem({
        id: 2,
        name: 'Mon autre venue',
      }),
    ]

    let offersRecap: CollectiveOfferResponseModel[]
    const stock: CollectiveOfferStockResponseModel = {
      bookingLimitDatetime: null,
      numberOfTickets: 100,
      price: 10,
    }

    beforeEach(() => {
      offersRecap = [collectiveOfferFactory({ stock })]
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue(offersRecap)
      vi.spyOn(router, 'useNavigate').mockReturnValue(
        routerUseNavigateReturnMock
      )
      vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
        offerersNames: [],
      })
      vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: proVenues })
      vi.spyOn(api, 'getOfferer').mockResolvedValue({
        ...defaultGetOffererResponseModel,
      })
    })

    afterEach(() => {
      window.sessionStorage.clear()
    })

    describe('url query params', () => {
      it('should have page value when page value is not first page', async () => {
        const offersRecap = Array.from({ length: 11 }, () =>
          collectiveOfferFactory({ stock })
        )
        vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)

        renderOffers()

        const nextPageIcon = await screen.findByRole('button', {
          name: /page suivante/,
        })

        await userEvent.click(nextPageIcon)

        expect(routerUseNavigateReturnMock).toHaveBeenCalledWith(
          '/offres/collectives?page=2',
          {
            replace: true,
          }
        )
      })

      it('should have offer name value when name search value is not an empty string', async () => {
        renderOffers()

        await userEvent.type(
          screen.getByRole('searchbox', {
            name: LABELS.nameSearchInput,
          }),
          'AnyWord'
        )
        await userEvent.click(screen.getByText('Rechercher'))

        expect(routerUseNavigateReturnMock).toHaveBeenCalledWith(
          '/offres/collectives?nom=AnyWord',
          {
            replace: true,
          }
        )
      })

      it('should have offer name value be removed when name search value is an empty string', async () => {
        renderOffers()

        await userEvent.clear(
          screen.getByRole('searchbox', {
            name: LABELS.nameSearchInput,
          })
        )
        await userEvent.click(screen.getByText('Rechercher'))

        expect(routerUseNavigateReturnMock).toHaveBeenCalledWith(
          '/offres/collectives',
          {
            replace: true,
          }
        )
      })

      it('should have venue value be removed when user asks for all venues', async () => {
        // Given
        vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)
        renderOffers()
        const firstTypeOption = screen.getByRole('option', {
          name: 'Concert',
        })
        const formatSelect = screen.getByRole('combobox', {
          name: 'Format',
        })
        // When
        await userEvent.selectOptions(formatSelect, firstTypeOption)
        await userEvent.click(screen.getByText('Rechercher'))

        expect(routerUseNavigateReturnMock).toHaveBeenCalledWith(
          '/offres/collectives?format=Concert',
          {
            replace: true,
          }
        )
      })

      it('should have the status in the url value when user filters by status', async () => {
        vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)
        renderOffers()

        await userEvent.click(
          screen.getByRole('button', {
            name: 'Statut',
          })
        )

        await userEvent.click(screen.getByText('Réservée'))

        await userEvent.click(
          screen.getByRole('button', { name: 'Rechercher' })
        )

        expect(routerUseNavigateReturnMock).toHaveBeenCalledWith(
          '/offres/collectives?statut=reservee',
          {
            replace: true,
          }
        )
      })

      it('should have the status in the url value when user filters by multiple statuses', async () => {
        vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)
        renderOffers()

        await userEvent.click(
          screen.getByRole('button', {
            name: 'Statut',
          })
        )

        await userEvent.click(screen.getByText('Réservée'))
        await userEvent.click(screen.getByText('En instruction'))
        await userEvent.click(screen.getByText('Archivée'))

        await userEvent.click(
          screen.getByRole('button', { name: 'Rechercher' })
        )

        expect(routerUseNavigateReturnMock).toHaveBeenCalledWith(
          '/offres/collectives?statut=reservee&statut=en-attente&statut=archivee',
          {
            replace: true,
          }
        )
      })
    })
  })

  describe('with WIP_SWITCH_VENUE feature flag', () => {
    const features = ['WIP_SWITCH_VENUE']

    it('should call getCollectiveOffers with the expected venueId', async () => {
      renderOffers({}, features)

      await waitFor(() => {
        expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
          null,
          offererId,
          null,
          2,
          null,
          null,
          null,
          null,
          null
        )
      })
    })
  })
})
