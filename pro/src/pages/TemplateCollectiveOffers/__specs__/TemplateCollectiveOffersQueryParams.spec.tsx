import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
  within,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  CollectiveOfferResponseModel,
  CollectiveOffersStockResponseModel,
} from 'apiClient/v1'
import { DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS } from 'commons/core/Offers/constants'
import { CollectiveSearchFiltersParams } from 'commons/core/Offers/types'
import { computeCollectiveOffersUrl } from 'commons/core/Offers/utils/computeCollectiveOffersUrl'
import { collectiveOfferFactory } from 'commons/utils/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  venueListItemFactory,
} from 'commons/utils/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'commons/utils/storeFactories'

import { TemplateCollectiveOffers } from '../TemplateCollectiveOffers'

vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useNavigate: vi.fn(),
}))

const renderOffers = async (
  filters: Partial<CollectiveSearchFiltersParams> = DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
  user = sharedCurrentUserFactory(),
  selectedOffererId: number | null = 1
) => {
  const shouldComputeTemplateOfferUrl = true
  const route = computeCollectiveOffersUrl(
    filters,
    DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
    shouldComputeTemplateOfferUrl
  )
  renderWithProviders(
    <router.Routes>
      <router.Route
        path="/offres/vitrines"
        element={<TemplateCollectiveOffers />}
      />
    </router.Routes>,
    {
      user,
      initialRouterEntries: [route],
      storeOverrides: {
        user: {
          selectedOffererId,
          currentUser: user,
        },
      },
    }
  )

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

  return {
    history,
  }
}

const proVenues = [
  venueListItemFactory({
    id: 1,
    name: 'Ma venue',
  }),
  venueListItemFactory({
    id: 2,
    name: 'Mon autre venue',
  }),
]

vi.mock('repository/venuesService', async () => ({
  ...(await vi.importActual('repository/venuesService')),
}))

describe('route TemplateCollectiveOffers', () => {
  let offersRecap: CollectiveOfferResponseModel[]
  const stocks: Array<CollectiveOffersStockResponseModel> = [
    {
      beginningDatetime: String(new Date()),
      hasBookingLimitDatetimePassed: false,
      remainingQuantity: 1,
    },
  ]
  const mockNavigate = vi.fn()

  beforeEach(() => {
    offersRecap = [collectiveOfferFactory({ stocks, isShowcase: true })]
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue(offersRecap)
    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: proVenues })
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
    })
  })

  describe('url query params', () => {
    it('should have page value when page value is not first page', async () => {
      const offersRecap = Array.from({ length: 11 }, () =>
        collectiveOfferFactory({ stocks })
      )
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)
      await renderOffers()
      const nextPageIcon = screen.getByRole('button', { name: 'Page suivante' })

      await userEvent.click(nextPageIcon)

      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/vitrines?page=2&structure=1',
        {
          replace: true,
        }
      )
    })

    it('should have offer name value when name search value is not an empty string', async () => {
      await renderOffers()

      await userEvent.type(
        screen.getByPlaceholderText('Rechercher par nom d’offre'),
        'AnyWord'
      )
      await userEvent.click(screen.getByText('Rechercher'))

      expect(mockNavigate).toHaveBeenCalledWith(
        `/offres/vitrines?nom-ou-isbn=AnyWord&structure=1`,
        {
          replace: true,
        }
      )
    })

    it('should have offer name value be removed when name search value is an empty string', async () => {
      await renderOffers()

      await userEvent.clear(
        screen.getByPlaceholderText('Rechercher par nom d’offre')
      )
      await userEvent.click(screen.getByText('Rechercher'))

      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/vitrines?structure=1',
        {
          replace: true,
        }
      )
    })

    it('should have venue value when user filters by venue', async () => {
      await renderOffers()
      await waitFor(() => {
        expect(api.getVenues).toHaveBeenCalledWith(null, null, 1)
      })
      const firstVenueOption = screen.getByRole('option', {
        name: proVenues[0].name,
      })
      const venueSelect = screen.getByLabelText('Lieu')

      await userEvent.selectOptions(venueSelect, firstVenueOption)
      await userEvent.click(screen.getByText('Rechercher'))

      expect(mockNavigate).toHaveBeenCalledWith(
        `/offres/vitrines?structure=1&lieu=${proVenues[0].id}`,
        {
          replace: true,
        }
      )
    })

    it('should have venue value be removed when user asks for all venues', async () => {
      // Given
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)
      await renderOffers()
      const firstTypeOption = screen.getByRole('option', {
        name: 'Concert',
      })
      const formatSelect = screen.getByRole('combobox', {
        name: 'Format',
      })
      // When
      await userEvent.selectOptions(formatSelect, firstTypeOption)
      await userEvent.click(screen.getByText('Rechercher'))

      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/vitrines?structure=1&format=Concert',
        {
          replace: true,
        }
      )
    })

    it('should have the status in the url value when user filters by status', async () => {
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)
      await renderOffers()

      await userEvent.click(
        screen.getByText('Statut', {
          selector: 'span',
        })
      )
      const list = screen.getByTestId('list')
      await userEvent.click(within(list).getByText('Publiée sur ADAGE'))

      await userEvent.click(screen.getByRole('button', { name: 'Rechercher' }))

      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/vitrines?structure=1&statut=active',
        {
          replace: true,
        }
      )
    })

    it('should have the status in the url value when user filters by multiple statuses', async () => {
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)
      await renderOffers()

      await userEvent.click(
        screen.getByText('Statut', {
          selector: 'span',
        })
      )
      const list = screen.getByTestId('list')
      await userEvent.click(within(list).getByText('En instruction'))
      await userEvent.click(within(list).getByText('Archivée'))

      await userEvent.click(screen.getByRole('button', { name: 'Rechercher' }))

      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/vitrines?structure=1&statut=en-attente&statut=archivee',
        {
          replace: true,
        }
      )
    })
  })
})
