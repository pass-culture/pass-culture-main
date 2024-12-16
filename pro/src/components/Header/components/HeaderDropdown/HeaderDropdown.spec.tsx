import { screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect } from 'vitest'

import {
  GetOffererNameResponseModel,
  GetOffererResponseModel,
} from 'apiClient/v1'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'commons/utils/factories/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

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
        offerer: {
          selectedOffererId: 1,
          offererNames: baseOfferersNames,
        },
      },
    }
  }
  renderWithProviders(<HeaderDropdown />, options)
}

describe('App', () => {
  it('should display structure name in alphabetical order', async () => {
    renderHeaderDropdown()

    await userEvent.click(screen.getByTestId('offerer-select'))
    await userEvent.click(screen.getByText(/Changer de structure/))

    const offererList = screen.getByTestId('offerers-selection-menu')
    const offerers = within(offererList).getAllByRole('menuitemradio')

    expect(offerers[0].textContent).toEqual('A Structure')
    expect(offerers[1].textContent).toEqual('B Structure')
  })

  describe('OA feature flag', () => {
    it('should display the right wording without the OA FF', async () => {
      renderHeaderDropdown()
      await userEvent.click(screen.getByTestId('offerer-select'))
      await waitFor(() => {
        expect(screen.getByTestId('offerer-header-label')).toBeInTheDocument()
      })

      const changeButton = screen.getByText('Changer de structure')
      expect(changeButton).toBeInTheDocument()
      await userEvent.click(changeButton)
      await waitFor(() => {
        expect(screen.getByText('Ajouter une nouvelle structure'))
      })
    })

    it('should display the right wording with the OA FF', async () => {
      renderHeaderDropdown({
        features: ['WIP_ENABLE_OFFER_ADDRESS'],
      })

      await userEvent.click(screen.getByTestId('offerer-select'))
      expect(
        screen.queryByTestId('offerer-header-label')
      ).not.toBeInTheDocument()

      const changeButton = screen.getByText('Changer')
      expect(changeButton).toBeInTheDocument()
      await userEvent.click(changeButton)
      await waitFor(() => {
        expect(screen.getByText('Ajouter'))
      })
    })
  })
})
