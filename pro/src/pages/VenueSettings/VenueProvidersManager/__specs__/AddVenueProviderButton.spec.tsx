import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { createRef } from 'react'

import { api } from '@/apiClient/api'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

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
      linkedProviders: [],
      selectSoftwareButtonRef: createRef(),
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
      {
        name: 'Ticket Ultra Mega Buster',
        id: 15,
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
    expect(options.length).toBe(5)

    expect(screen.getByRole('option', { name: 'Allociné' })).toBeInTheDocument()
    expect(
      screen.getByRole('option', { name: 'Ticket Buster' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('option', { name: 'Ciné Office' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('option', { name: 'Ticket Ultra Mega Buster' })
    ).toBeInTheDocument()
  })

  it('should display the provider details on click', async () => {
    await renderAddVenueProviderButton(props)

    const addVenueProviderButton = screen.getByText('Sélectionner un logiciel')
    expect(addVenueProviderButton).toBeInTheDocument()
    await userEvent.click(addVenueProviderButton)
    const options = screen.getAllByRole('option')
    expect(options.length).toBe(5)

    const providerSelect = screen.getByTestId('provider-select')

    await userEvent.selectOptions(providerSelect, 'Ticket Buster')
    expect(screen.getByTestId('stocks-provider-form')).toBeInTheDocument()

    await userEvent.selectOptions(providerSelect, 'Ticket Ultra Mega Buster')
    expect(screen.getByTestId('stocks-provider-form')).toBeInTheDocument()
  })

  it('should hide linked providers', async () => {
    await renderAddVenueProviderButton({
      ...props,
      linkedProviders: [
        {
          name: 'Ticket Buster',
          id: 14,
          hasOffererProvider: true,
          isActive: true,
        },
      ],
    })

    const addVenueProviderButton = screen.getByText('Sélectionner un logiciel')
    expect(addVenueProviderButton).toBeInTheDocument()
    await userEvent.click(addVenueProviderButton)
    const options = screen.getAllByRole('option')
    expect(options.length).toBe(4)

    expect(screen.getByRole('option', { name: 'Allociné' })).toBeInTheDocument()
    expect(
      screen.getByRole('option', { name: 'Ciné Office' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('option', { name: 'Ticket Ultra Mega Buster' })
    ).toBeInTheDocument()
  })

  it('should hide other integrated providers if venue is already linked to an integrated provider', async () => {
    await renderAddVenueProviderButton({
      ...props,
      linkedProviders: [
        {
          name: 'Allociné',
          id: 13,
          hasOffererProvider: false,
          isActive: true,
        },
      ],
    })

    const addVenueProviderButton = screen.getByText('Sélectionner un logiciel')
    expect(addVenueProviderButton).toBeInTheDocument()
    await userEvent.click(addVenueProviderButton)
    const options = screen.getAllByRole('option')
    expect(options.length).toBe(3)

    expect(
      screen.getByRole('option', { name: 'Ticket Buster' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('option', { name: 'Ticket Ultra Mega Buster' })
    ).toBeInTheDocument()
  })
})
