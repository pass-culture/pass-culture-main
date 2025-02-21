import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { defaultGetVenue } from 'commons/utils/factories/collectiveApiFactories'
import { defaultVenueProvider } from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import {
  AllocineProviderEdit,
  AllocineProviderEditProps,
} from '../AllocineProviderEdit'

const renderAllocineProviderEdit = async (props: AllocineProviderEditProps) => {
  renderWithProviders(<AllocineProviderEdit {...props} />)

  await waitFor(() => screen.getByText('Paramétrer'))
}

describe('AllocineProviderEdit', () => {
  let props: AllocineProviderEditProps
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
    await renderAllocineProviderEdit(props)

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
    expect(screen.getByText('Prix de vente/place *')).toBeInTheDocument()
  })

  it('should update venue on submit', async () => {
    props.venueProvider = {
      ...props.venueProvider,
      quantity: 2,
      price: 2,
    }
    await renderAllocineProviderEdit(props)

    const editButton = screen.getByRole('button', { name: 'Paramétrer' })

    expect(editButton).toBeInTheDocument()
    await userEvent.click(editButton)
    const editValidationButton = screen.getByRole('button', {
      name: 'Modifier',
    })

    expect(editValidationButton).toBeInTheDocument()
    await userEvent.click(editValidationButton)
    expect(api.updateVenueProvider).toHaveBeenCalledTimes(1)
  })
})
