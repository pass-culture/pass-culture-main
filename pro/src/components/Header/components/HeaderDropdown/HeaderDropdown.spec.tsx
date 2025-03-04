import { screen, within, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect } from 'vitest'

import { api } from 'apiClient/api'
import {
  GetOffererNameResponseModel,
  GetOffererResponseModel,
} from 'apiClient/v1'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'commons/utils/factories/individualApiFactories'
import { currentOffererFactory } from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'
import { locallyStoredFilterConfig } from 'components/OffersTable/OffersTableSearch/utils'

import { HeaderDropdown } from './HeaderDropdown'

const baseOfferers: GetOffererResponseModel[] = [
  {
    ...defaultGetOffererResponseModel,
    id: 1,
    name: 'B Structure',
    isActive: true,
    hasDigitalVenueAtLeastOneOffer: true,
    managedVenues: [
      {
        ...defaultGetOffererVenueResponseModel,
        id: 1,
        isVirtual: true,
      },
    ],
    hasValidBankAccount: false,
  },
  {
    ...defaultGetOffererResponseModel,
    id: 2,
    name: 'A Structure',
    hasValidBankAccount: true,
  },
]

const baseOfferersNames = baseOfferers.map(
  (offerer): GetOffererNameResponseModel => ({
    id: offerer.id,
    name: offerer.name,
    allowedOnAdage: true,
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
      },
    }
  }
  renderWithProviders(<HeaderDropdown />, options)
}

describe('App', () => {
  it('should display structure name in alphabetical order', async () => {
    renderHeaderDropdown()

    await userEvent.click(screen.getByTestId('offerer-select'))
    await userEvent.click(screen.getByText(/Changer/))

    const offererList = screen.getByTestId('offerers-selection-menu')
    const offerers = within(offererList).getAllByRole('menuitemradio')

    expect(offerers[0].textContent).toEqual('A Structure')
    expect(offerers[1].textContent).toEqual('B Structure')
  })

  describe('Switch Offerer', () => {
    beforeEach(() => {
      vi.mock('apiClient/api', () => ({
        api: {
          getOfferer: vi.fn(),
        },
      }))

      vi.spyOn(api, 'getOfferer').mockResolvedValue(
        defaultGetOffererResponseModel
      )
    })

    it('should call "handleChangeOfferer" on value change', async () => {
      renderHeaderDropdown()

      // Opens main menu
      await userEvent.click(screen.getByTestId('offerer-select'))

      // Opens sub-menu
      await userEvent.click(screen.getByText(/Changer/))

      // Get structures list
      const offererList = screen.getByTestId('offerers-selection-menu')
      const offerers = within(offererList).getAllByRole('menuitemradio')

      await userEvent.click(offerers[0])

      expect(api.getOfferer).toHaveBeenCalledOnce()
    })

    it('should reset url query parameters & stored search filters', async () => {
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
      await userEvent.click(screen.getByTestId('offerer-select'))

      // Opens sub-menu
      await userEvent.click(screen.getByText(/Changer/))

      // Get structures list
      const offererList = screen.getByTestId('offerers-selection-menu')
      const offerers = within(offererList).getAllByRole('menuitemradio')

      // Clic on one structure
      await userEvent.click(offerers[0])

      await waitFor(() => {
        expect(api.getOfferer).toHaveBeenCalledOnce()
      })

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
  })
})
