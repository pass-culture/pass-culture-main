import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router'

import { api } from '@/apiClient/api'
import type {
  CollectiveOfferTemplateResponseModel,
  GetOffererAddressResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'
import { DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { collectiveOfferTemplateFactory } from '@/commons/utils/factories/collectiveApiFactories'
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

import { TemplateCollectiveOffers } from '../TemplateCollectiveOffers'

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useNavigate: vi.fn(),
}))

vi.mock('@/commons/hooks/useActiveFeature', () => ({
  useActiveFeature: vi.fn(),
}))

const mockVenuesResponse: { venues: VenueListItemResponseModel[] } = {
  venues: [
    makeVenueListItem({
      id: 1,
      name: 'First Venue',
      isPermanent: true,
      hasCreatedOffer: true,
    }),
    makeVenueListItem({
      id: 2,
      name: 'Second Venue',
      isPermanent: true,
      hasCreatedOffer: true,
    }),
  ],
}

vi.mock('@/apiClient/api', () => {
  return {
    api: {
      getCollectiveOfferTemplates: vi.fn(),
      getOfferer: vi.fn(),
      listOfferersNames: vi.fn(),
      getVenues: vi.fn(() => mockVenuesResponse),
      getOffererAddresses: vi.fn(),
    },
  }
})

const renderOffers = async (
  filters: Partial<CollectiveSearchFiltersParams> = DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
  user = sharedCurrentUserFactory()
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
          currentUser: user,
          selectedVenue: makeVenueListItem({ id: 2 }),
        },
        offerer: currentOffererFactory(),
      },
    }
  )

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

  return {
    history,
  }
}

vi.mock('repository/venuesService', async () => ({
  ...(await vi.importActual('repository/venuesService')),
}))

describe('route TemplateCollectiveOffers', () => {
  let offersRecap: CollectiveOfferTemplateResponseModel[]

  const offererAddress: GetOffererAddressResponseModel[] = [
    offererAddressFactory({
      label: 'Label',
    }),
    offererAddressFactory({
      city: 'New York',
    }),
  ]

  const mockNavigate = vi.fn()

  beforeEach(() => {
    offersRecap = [collectiveOfferTemplateFactory()]
    vi.spyOn(api, 'getCollectiveOfferTemplates').mockResolvedValue(offersRecap)
    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
    })
    vi.spyOn(api, 'getOffererAddresses').mockResolvedValue(offererAddress)
  })

  afterEach(() => {
    window.sessionStorage.clear()
  })

  describe('url query params', () => {
    // Necessary because JSDOM doesn't implement the `scrollTo` method
    // (which is used by the `useAccessibleScroll` hook in that component's scope)
    beforeAll(() => {
      Element.prototype.scrollTo = () => {}
      window.scrollTo = () => {}
    })

    it('should have page value when page value is not first page', async () => {
      const offersRecap = Array.from({ length: 11 }, () =>
        collectiveOfferTemplateFactory()
      )
      vi.spyOn(api, 'getCollectiveOfferTemplates').mockResolvedValueOnce(
        offersRecap
      )
      await renderOffers()
      const nextPageIcon = screen.getByRole('button', { name: /page suivante/ })

      await userEvent.click(nextPageIcon)

      expect(mockNavigate).toHaveBeenCalledWith('/offres/vitrines?page=2', {
        replace: true,
      })
    })

    it('should have offer name value when name search value is not an empty string', async () => {
      await renderOffers()

      await userEvent.type(
        screen.getByRole('searchbox', {
          name: 'Nom de l’offre',
        }),
        'AnyWord'
      )
      await userEvent.click(screen.getByText('Rechercher'))

      expect(mockNavigate).toHaveBeenCalledWith(
        `/offres/vitrines?nom=AnyWord`,
        {
          replace: true,
        }
      )
    })

    it('should have offer name value be removed when name search value is an empty string', async () => {
      await renderOffers()

      await userEvent.clear(
        screen.getByRole('searchbox', {
          name: 'Nom de l’offre',
        })
      )
      await userEvent.click(screen.getByText('Rechercher'))

      expect(mockNavigate).toHaveBeenCalledWith('/offres/vitrines', {
        replace: true,
      })
    })

    it('should have venue value be removed when user asks for all venues', async () => {
      // Given
      vi.spyOn(api, 'getCollectiveOfferTemplates').mockResolvedValueOnce(
        offersRecap
      )
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
        '/offres/vitrines?format=Concert',
        {
          replace: true,
        }
      )
    })

    it('should have the status in the url value when user filters by one status', async () => {
      vi.spyOn(api, 'getCollectiveOfferTemplates').mockResolvedValueOnce(
        offersRecap
      )
      await renderOffers()

      await userEvent.click(
        screen.getByRole('button', {
          name: 'Statut',
        })
      )
      await userEvent.click(screen.getByText('Publiée sur ADAGE'))

      await userEvent.click(screen.getByRole('button', { name: 'Rechercher' }))

      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/vitrines?statut=active',
        {
          replace: true,
        }
      )
    })

    it('should have the status in the url value when user filters by multiple statuses', async () => {
      vi.spyOn(api, 'getCollectiveOfferTemplates').mockResolvedValueOnce(
        offersRecap
      )
      await renderOffers()

      await userEvent.click(
        screen.getByRole('button', {
          name: 'Statut',
        })
      )
      await userEvent.click(screen.getByText('En instruction'))
      await userEvent.click(screen.getByText('Archivée'))

      await userEvent.click(screen.getByRole('button', { name: 'Rechercher' }))

      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/vitrines?statut=en-attente&statut=archivee',
        {
          replace: true,
        }
      )
    })

    const getMockedAddresses = () => [
      offererAddressFactory({ label: 'Label' }),
      offererAddressFactory({ city: 'New York' }),
    ]

    const setupAddresses = () => {
      const offererAddress = getMockedAddresses()
      vi.spyOn(api, 'getOffererAddresses').mockResolvedValue(offererAddress)
      return offererAddress
    }

    it('should have locationType value in the url when user filters by localisation', async () => {
      setupAddresses()
      await renderOffers()
      await userEvent.selectOptions(screen.getByLabelText('Localisation'), [
        await screen.findByRole('option', {
          name: 'En établissement scolaire',
        }),
      ])
      await userEvent.click(screen.getByText('Rechercher'))
      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/vitrines?locationType=SCHOOL',
        { replace: true }
      )
    })

    it('should have offererAddressId value in the url when user filters by address', async () => {
      setupAddresses()
      await renderOffers()
      const option = await screen.findByRole('option', {
        name: 'Label - 1 Rue de paris 75001 Paris',
      })
      await userEvent.selectOptions(screen.getByLabelText('Localisation'), [
        option,
      ])
      await userEvent.click(screen.getByText('Rechercher'))

      expect(mockNavigate).toHaveBeenCalledWith(
        `/offres/vitrines?locationType=ADDRESS&offererAddressId=5`,
        { replace: true }
      )
    })

    it('should remove locationType and offererAddressId from url when user selects "Toutes"', async () => {
      setupAddresses()
      await renderOffers()
      await userEvent.selectOptions(screen.getByLabelText('Localisation'), [
        await screen.findByRole('option', { name: 'Toutes' }),
      ])
      await userEvent.click(screen.getByText('Rechercher'))
      expect(mockNavigate).toHaveBeenCalledWith('/offres/vitrines', {
        replace: true,
      })
    })

    it('should have locationType value in the url when user filters by "À déterminer"', async () => {
      setupAddresses()
      await renderOffers()
      const option = await screen.findByRole('option', {
        name: 'À déterminer',
      })
      await userEvent.selectOptions(screen.getByLabelText('Localisation'), [
        option,
      ])
      await userEvent.click(screen.getByText('Rechercher'))
      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/vitrines?locationType=TO_BE_DEFINED',
        { replace: true }
      )
    })
  })
})
