import { screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import {
  GetOffererNameResponseModel,
  GetOffererResponseModel,
} from 'apiClient/v1'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { HeaderDropdown } from '../HeaderDropdown/HeaderDropdown'

const renderHeaderDropdown = () => {
  renderWithProviders(<HeaderDropdown />)
}

describe('App', () => {
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
  beforeEach(() => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: baseOfferersNames,
    })
  })
  it('should display structure name in alphabetical order', async () => {
    renderHeaderDropdown()

    await userEvent.click(screen.getByTestId('offerer-select'))
    await userEvent.click(screen.getByText(/Changer de structure/))

    const offererList = screen.getByTestId('offerers-selection-menu')
    const offerers = within(offererList).getAllByRole('menuitemradio')

    expect(offerers[0].textContent).toEqual('A Structure')
    expect(offerers[1].textContent).toEqual('B Structure')
  })
})
