import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { defaultGetVenue } from 'commons/utils/factories/collectiveApiFactories'
import { defaultVenueProvider } from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import {
  CinemaProviderEdit,
  CinemaProviderEditProps,
} from '../CinemaProviderEdit'

const renderCinemaProviderEdit = async (props: CinemaProviderEditProps) => {
  renderWithProviders(<CinemaProviderEdit {...props} />)

  await waitFor(() => screen.getByText('Paramétrer'))
}

describe('CinemaProviderEdit', () => {
  let props: CinemaProviderEditProps
  const offererId = 3

  beforeEach(() => {
    props = {
      offererId: offererId,
      venue: defaultGetVenue,
      venueProvider: defaultVenueProvider,
    }
    vi.spyOn(api, 'updateVenueProvider').mockResolvedValue(defaultVenueProvider)
  })

  it('should display functional edit button', async () => {
    await renderCinemaProviderEdit(props)

    const editButton = screen.getByRole('button', { name: 'Paramétrer' })
    expect(editButton).toBeInTheDocument()

    await userEvent.click(editButton)
    expect(
      screen.getByText('Modifier les paramètres de vos offres')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Accepter les réservations duo')
    ).toBeInTheDocument()

    const isDuoCheckbox = screen.getByLabelText(/Accepter les réservations duo/)
    expect(isDuoCheckbox).toBeInTheDocument()
    expect(isDuoCheckbox).toBeChecked()
  })

  it('should update venue on submit', async () => {
    await renderCinemaProviderEdit(props)

    const editButton = screen.getByRole('button', { name: 'Paramétrer' })
    expect(editButton).toBeInTheDocument()

    await userEvent.click(editButton)
    expect(
      screen.getByText('Modifier les paramètres de vos offres')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Accepter les réservations duo')
    ).toBeInTheDocument()

    const isDuoCheckbox = screen.getByLabelText(/Accepter les réservations duo/)
    expect(isDuoCheckbox).toBeInTheDocument()
    expect(isDuoCheckbox).toBeChecked()

    const submitButton = screen.getByRole('button', { name: 'Modifier' })
    await userEvent.click(submitButton)
    expect(api.updateVenueProvider).toHaveBeenCalledTimes(1)
  })
})
