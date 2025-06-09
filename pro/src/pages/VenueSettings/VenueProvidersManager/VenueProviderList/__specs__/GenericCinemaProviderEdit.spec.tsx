import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { defaultGetVenue } from 'commons/utils/factories/collectiveApiFactories'
import { defaultVenueProvider } from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import {
  GenericCinemaProviderEdit,
  GenericCinemaProviderEditProps,
} from '../GenericCinemaProviderEdit'

vi.mock('commons/hooks/useNotification', () => ({
  useNotification: () => ({
    success: vi.fn(),
    error: vi.fn(),
  }),
}))

describe('GenericCinemaProviderEdit', () => {
  const offererId = 3
  let props: GenericCinemaProviderEditProps

  beforeEach(() => {
    props = {
      offererId,
      venue: defaultGetVenue,
      venueProvider: defaultVenueProvider,
      showAdvancedFields: false,
    }

    vi.spyOn(api, 'updateVenueProvider').mockResolvedValue(defaultVenueProvider)
  })

  const renderComponent = async () => {
    renderWithProviders(<GenericCinemaProviderEdit {...props} />)
    const paramButton = screen.getByRole('button', { name: 'Paramétrer' })
    expect(paramButton).toBeInTheDocument()
    await userEvent.click(paramButton)
    await waitFor(() =>
      expect(
        screen.getByText('Modifier les paramètres de vos offres')
      ).toBeInTheDocument()
    )
  }

  it('should open dialog and display form with isDuo checkbox checked', async () => {
    await renderComponent()

    expect(
      screen.getByText('Accepter les réservations “Duo“')
    ).toBeInTheDocument()

    const isDuoCheckbox = screen.getByLabelText(
      /Accepter les réservations “Duo“/
    )
    expect(isDuoCheckbox).toBeChecked()
  })

  it('should submit updated provider values on form submit', async () => {
    await renderComponent()

    const submitButton = screen.getByRole('button', { name: 'Modifier' })
    expect(submitButton).toBeInTheDocument()

    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(api.updateVenueProvider).toHaveBeenCalledWith({
        providerId: defaultVenueProvider.provider.id,
        venueId: defaultVenueProvider.venueId,
        isDuo: defaultVenueProvider.isDuo,
        isActive: defaultVenueProvider.isActive,
      })
    })
  })

  it('should allow toggling isDuo checkbox', async () => {
    await renderComponent()

    const isDuoCheckbox = screen.getByLabelText(
      /Accepter les réservations “Duo“/
    )
    expect(isDuoCheckbox).toBeChecked()

    await userEvent.click(isDuoCheckbox)
    expect(isDuoCheckbox).not.toBeChecked()
  })
})
