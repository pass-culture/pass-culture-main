import { screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect } from 'vitest'

import { api } from '@/apiClient/api'
import type {
  GetOffererNameResponseModel,
  GetOffererResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
  getOffererNameFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { currentOffererFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { locallyStoredFilterConfig } from '@/components/OffersTableSearch/utils'

import { HeaderDropdown } from './HeaderDropdown'

const baseOfferers: GetOffererResponseModel[] = [
  {
    ...defaultGetOffererResponseModel,
    id: 1,
    name: 'Offerer A',
    isActive: true,
    hasDigitalVenueAtLeastOneOffer: true,
    managedVenues: [
      {
        ...defaultGetOffererVenueResponseModel,
        id: 3,
        isVirtual: true,
        name: 'Digital Venue A1',
      },
    ],
    hasValidBankAccount: false,
  },
  {
    ...defaultGetOffererResponseModel,
    id: 2,
    name: 'Offerer B',
    hasValidBankAccount: true,
  },
]
const baseVenues: VenueListItemResponseModel[] = [
  makeVenueListItem({
    id: 3,
    managingOffererId: 1,
    name: 'Digital Venue A1',
  }),
  makeVenueListItem({
    id: 4,
    managingOffererId: 2,
    name: 'Digital Venue B1',
  }),
]

const baseOfferersNames = baseOfferers.map(
  (offerer): GetOffererNameResponseModel => ({
    id: offerer.id,
    name: offerer.name,
  })
)
const renderHeaderDropdown = (options?: RenderWithProvidersOptions) => {
  if (!options?.storeOverrides?.offerer) {
    options = {
      ...options,
      storeOverrides: {
        ...options?.storeOverrides,
        offerer: currentOffererFactory({
          offererNames: baseOfferersNames,
        }),
        user: {
          ...options?.storeOverrides?.user,
          venues: baseVenues,
        },
      },
      features: [],
    }
  }
  renderWithProviders(<HeaderDropdown />, options)
}

describe('App', () => {
  describe('without WIP_SWITCH_VENUE feature flag', () => {
    it('should display structure name in alphabetical order', async () => {
      renderHeaderDropdown()

      await userEvent.click(screen.getByTestId('profile-button'))
      await userEvent.click(screen.getByText(/Changer/))

      const offererList = screen.getByTestId('offerers-selection-menu')
      const offerers = within(offererList).getAllByRole('menuitemradio')

      expect(offerers[0].textContent).toEqual('Offerer A')
      expect(offerers[1].textContent).toEqual('Offerer B')
    })
  })
  describe('with WIP_SWITCH_VENUE feature flag', () => {
    it('should display not display the switch button', async () => {
      const features = ['WIP_SWITCH_VENUE']
      const renderHeaderDropdownWithSwitchVenue = (
        options?: RenderWithProvidersOptions
      ) => {
        if (!options?.storeOverrides?.offerer) {
          options = {
            ...options,
            storeOverrides: {
              ...options?.storeOverrides,
              offerer: currentOffererFactory({
                offererNames: baseOfferersNames,
              }),
              user: {
                ...options?.storeOverrides?.user,
                venues: baseVenues,
              },
            },
            features: features,
          }
        }
        renderWithProviders(<HeaderDropdown />, options)
      }

      renderHeaderDropdownWithSwitchVenue()
      await userEvent.click(screen.getByTestId('profile-button'))

      expect(screen.queryByText(/Changer/)).toBeNull()
    })
  })
})
describe('Switch Offerer', () => {
  beforeEach(() => {
    vi.mock('@/apiClient/api', () => ({
      api: {
        getOfferer: vi.fn(),
        signout: vi.fn(),
      },
    }))

    vi.spyOn(api, 'getOfferer').mockResolvedValue(
      defaultGetOffererResponseModel
    )
  })

  it('should reset url query parameters & stored search filters', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    // Mock sessionStorage state to simulate previously stored search filters.
    const filtersVisibilityForAll = true
    Object.values(locallyStoredFilterConfig).forEach((key) => {
      sessionStorage.setItem(
        key,
        JSON.stringify({
          filtersVisibility: filtersVisibilityForAll,
          storedFilters: {
            categoryId: 1,
            venueId: 1,
          },
        })
      )
    })

    renderHeaderDropdown({
      initialRouterEntries: ['/offres?categorie=CINEMA&offererAddressId=1'],
    })

    // Opens main menu
    await userEvent.click(screen.getByTestId('profile-button'))

    // Opens sub-menu
    await userEvent.click(screen.getByText(/Changer/))

    // Get structures list
    const offererList = screen.getByTestId('offerers-selection-menu')
    const offerers = within(offererList).getAllByRole('menuitemradio')

    // Clic on one structure
    await userEvent.click(offerers[0])

    // Stored search filters should be reset, while filters
    // visibility must be remembered.
    Object.values(locallyStoredFilterConfig).forEach((key) => {
      const storedConfiguration = JSON.parse(
        sessionStorage.getItem(key) || '{}'
      )
      const { filtersVisibility, storedFilters } = storedConfiguration

      expect(storedFilters).toEqual({})
      expect(filtersVisibility).toEqual(filtersVisibilityForAll)
    })

    sessionStorage.clear()
  })

  it('should display add a venue button when only one offerer', async () => {
    const options = {
      storeOverrides: {
        offerer: {
          offererNames: [
            getOffererNameFactory({
              id: 1,
              name: 'Mon offerer',
            }),
          ],
          currentOffererName: getOffererNameFactory({
            id: 1,
            name: 'Mon offerer',
          }),
        },
      },
    }
    renderWithProviders(<HeaderDropdown />, options)

    // Opens main menu
    await userEvent.click(screen.getByTestId('profile-button'))

    expect(screen.getByText(/Mon offerer/)).toBeInTheDocument()
    expect(screen.getByText(/Ajouter une structure/)).toBeInTheDocument()
  })
})
