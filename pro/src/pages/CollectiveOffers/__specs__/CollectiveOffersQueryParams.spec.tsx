import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router'

import { api } from '@/apiClient/api'
import type {
  CollectiveOfferResponseModel,
  CollectiveOfferStockResponseModel,
} from '@/apiClient/v1'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { collectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOffers } from '../CollectiveOffers'

//FIX ME : extract inital values and constant to reduce code duplication with CollectiveOffers.spec.tsx

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useNavigate: vi.fn(),
}))

const LABELS = {
  nameSearchInput: /Nom de l’offre/,
}

const renderOffers = (
  filters: Partial<CollectiveSearchFiltersParams> = DEFAULT_COLLECTIVE_SEARCH_FILTERS
) => {
  const route = computeCollectiveOffersUrl(filters)
  renderWithProviders(
    <router.Routes>
      <router.Route path="/offres/collectives" element={<CollectiveOffers />} />

      <router.Route path="/offres" element={<h1>Offres individuelles</h1>} />
    </router.Routes>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: [route],
      storeOverrides: {
        offerer: {
          currentOfferer: { id: 1, isOnboarded: true },
          offererNames: [],
        },
        user: {
          selectedVenue: makeVenueListItem({ id: 2 }),
        },
      },
    }
  )

  return {
    history,
  }
}

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

vi.mock('@/apiClient/api', () => {
  return {
    api: {
      getCollectiveOffers: vi.fn(),
      getOfferer: vi.fn(),
      listOfferersNames: vi.fn(),
      getVenues: vi.fn(),
      getOffererAddresses: vi.fn(),
    },
  }
})

vi.mock('repository/venuesService', async () => ({
  ...(await vi.importActual('repository/venuesService')),
}))

describe('CollectiveOffersQueryParams', () => {
  let offersRecap: CollectiveOfferResponseModel[]
  const stock: CollectiveOfferStockResponseModel = {
    bookingLimitDatetime: null,
    numberOfTickets: 100,
    price: 10,
  }

  const mockNavigate = vi.fn()

  beforeEach(() => {
    offersRecap = [collectiveOfferFactory({ stock })]
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue(offersRecap)
    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
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

      expect(mockNavigate).toHaveBeenCalledWith('/offres/collectives?page=2', {
        replace: true,
      })
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

      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/collectives?nom-ou-isbn=AnyWord',
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

      expect(mockNavigate).toHaveBeenCalledWith('/offres/collectives', {
        replace: true,
      })
    })

    it('should have venue value be removed when user asks for all venues', async () => {
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)
      renderOffers()
      const firstTypeOption = screen.getByRole('option', {
        name: 'Concert',
      })
      const formatSelect = screen.getByRole('combobox', {
        name: 'Format',
      })

      await userEvent.selectOptions(formatSelect, firstTypeOption)
      await userEvent.click(screen.getByText('Rechercher'))

      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/collectives?format=Concert',
        {
          replace: true,
        }
      )
    })

    it('should have the status in the url value when user filters by status', async () => {
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)
      renderOffers()

      await userEvent.click(screen.getByRole('button', { name: 'Statut' }))

      await userEvent.click(screen.getByText('Réservée'))

      await userEvent.click(screen.getByRole('button', { name: 'Rechercher' }))

      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/collectives?statut=reservee',
        { replace: true }
      )
    })

    it('should have the status in the url value when user filters by multiple statuses', async () => {
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)
      renderOffers()

      await userEvent.click(screen.getByRole('button', { name: 'Statut' }))
      await userEvent.click(screen.getByText('Réservée'))
      await userEvent.click(screen.getByText('En instruction'))
      await userEvent.click(screen.getByText('Archivée'))

      await userEvent.click(screen.getByRole('button', { name: 'Rechercher' }))

      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/collectives?statut=reservee&statut=en-attente&statut=archivee',
        { replace: true }
      )
    })
  })
})
