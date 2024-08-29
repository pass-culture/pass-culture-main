import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { defaultGetVenue } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  AddVenueProviderButton,
  AddVenueProviderButtonProps,
} from '../AddVenueProviderButton'

const renderAddVenueProviderButton = async (
  props: AddVenueProviderButtonProps
) => {
  renderWithProviders(<AddVenueProviderButton {...props} />)
  await waitFor(() => {
    screen.getByText('Sélectionner un logiciel')
  })
}

describe('AddVenueProviderButton', () => {
  let props: AddVenueProviderButtonProps

  beforeEach(() => {
    props = {
      venue: defaultGetVenue,
      linkedProvidersIds: [],
    }

    vi.spyOn(api, 'getProvidersByVenue').mockResolvedValue([
      {
        name: 'Ciné Office',
        id: 12,
        hasOffererProvider: false,
        isActive: true,
      },
      {
        name: 'Allociné',
        id: 13,
        hasOffererProvider: false,
        isActive: true,
      },
      {
        name: 'Ticket Buster',
        id: 14,
        hasOffererProvider: true,
        isActive: true,
      },
    ])
  })

  it('should display the add button', async () => {
    await renderAddVenueProviderButton(props)

    const addVenueProviderButton = screen.getByText('Sélectionner un logiciel')
    expect(addVenueProviderButton).toBeInTheDocument()
  })

  it('should display the providers on click', async () => {
    await renderAddVenueProviderButton(props)

    const addVenueProviderButton = screen.getByText('Sélectionner un logiciel')
    expect(addVenueProviderButton).toBeInTheDocument()
    await userEvent.click(addVenueProviderButton)
    const options = screen.getAllByRole('option')
    expect(options.length).toBe(4)

    expect(screen.getByRole('option', { name: 'Allociné' })).toBeInTheDocument()
    expect(
      screen.getByRole('option', { name: 'Ticket Buster' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('option', { name: 'Ciné Office' })
    ).toBeInTheDocument()
  })

  it('should hide linked providers', async () => {
    await renderAddVenueProviderButton({
      ...props,
      linkedProvidersIds: [12, 14],
    })

    const addVenueProviderButton = screen.getByText('Sélectionner un logiciel')
    expect(addVenueProviderButton).toBeInTheDocument()
    await userEvent.click(addVenueProviderButton)
    const options = screen.getAllByRole('option')
    expect(options.length).toBe(2)

    expect(screen.getByRole('option', { name: 'Allociné' })).toBeInTheDocument()
  })
})
