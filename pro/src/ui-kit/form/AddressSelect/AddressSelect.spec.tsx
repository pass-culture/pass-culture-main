import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { AdresseData } from '@/apiClient//adresse/types'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { AddressSelect, AddressSelectProps } from './AddressSelect'

const renderAddressSelect = (
  Component: React.ReactNode,
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(Component, { ...options })
}

const defaultProps: AddressSelectProps = {
  name: 'addressText',
  label: 'Adresse postale',
}

const mockAPIResponse: AdresseData[] = [
  {
    address: "17 Rue d'Abbeville",
    city: 'Amiens',
    id: '80021_0050_00017',
    latitude: 49.905915,
    longitude: 2.270522,
    label: "17 Rue d'Abbeville 80000 Amiens",
    postalCode: '80000',
    inseeCode: '80021',
  },
  {
    address: "17 Rue d'Entraigues",
    city: 'Tours',
    id: '37261_1680_00017',
    latitude: 47.388071,
    longitude: 0.688431,
    label: "17 Rue d'Entraigues 37000 Tours",
    postalCode: '37000',
    inseeCode: '37261',
  },
  {
    address: "17 Rue d'Artois",
    city: 'Lille',
    id: '59350_0391_00017',
    latitude: 50.62467,
    longitude: 3.061394,
    label: "17 Rue d'Artois 59000 Lille",
    postalCode: '59000',
    inseeCode: '59350',
  },
  {
    address: "17 Rue d'Auxonne",
    city: 'Dijon',
    id: '21231_0610_00017',
    latitude: 47.315591,
    longitude: 5.045492,
    label: "17 Rue d'Auxonne 21000 Dijon",
    postalCode: '21000',
    inseeCode: '21231',
  },
  {
    address: "17 Rue d'Assalit",
    city: 'Toulouse',
    id: '31555_0580_00017',
    latitude: 43.60356,
    longitude: 1.469539,
    label: "17 Rue d'Assalit 31500 Toulouse",
    postalCode: '31500',
    inseeCode: '31555',
  },
]

const getDataFromAddressMock = vi.hoisted(() => vi.fn())

vi.mock('@/apiClient//api', () => ({
  getDataFromAddress: getDataFromAddressMock,
}))

describe('<AddressSelect />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderAddressSelect(
      <AddressSelect {...defaultProps} />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render with description', () => {
    renderAddressSelect(
      <AddressSelect
        {...defaultProps}
        description="Uniquement si vous souhaitez préciser l’adresse exacte"
      />
    )

    expect(screen.getByTestId('description-addressText')).toHaveTextContent(
      'Uniquement si vous souhaitez préciser l’adresse exacte'
    )
  })

  it('should call "getDataFromAddress" internally with the correct parameters', async () => {
    renderAddressSelect(
      <AddressSelect
        {...defaultProps}
        onlyTypes={['municipality', 'street']}
        suggestionLimit={35}
      />
    )

    const input = screen.getByRole('combobox', { name: 'Adresse postale *' })

    const user = userEvent.setup()
    await user.click(input)
    await user.type(input, 'Tou')

    await waitFor(() => {
      expect(getDataFromAddressMock).toHaveBeenCalledExactlyOnceWith('Tou', {
        limit: 35,
        onlyTypes: ['municipality', 'street'],
      })
    })
  })

  it('should display the correct address suggestions', async () => {
    getDataFromAddressMock.mockResolvedValue(mockAPIResponse)

    renderAddressSelect(<AddressSelect {...defaultProps} />)

    const input = screen.getByRole('combobox', { name: 'Adresse postale *' })

    const user = userEvent.setup()
    await user.click(input)
    await user.type(input, "17 rue d'")

    expect(await screen.findAllByRole('option')).toHaveLength(
      mockAPIResponse.length
    )

    await user.clear(input)
    await user.type(input, "17 rue d'A") // "17 Rue d'Entraigues 37000 Tours" shouldn't be part of the suggestions

    expect(await screen.findAllByRole('option')).toHaveLength(
      mockAPIResponse.length - 1
    )
  })

  it('should call "onAddressChosen" with the correct address when an address is selected', async () => {
    const onAddressChosen = vi.fn()
    getDataFromAddressMock.mockResolvedValue(mockAPIResponse)

    renderAddressSelect(
      <AddressSelect {...defaultProps} onAddressChosen={onAddressChosen} />
    )

    const input = screen.getByRole('combobox', { name: 'Adresse postale *' })

    const user = userEvent.setup()
    await user.click(input)
    await user.type(input, "17 rue d'")

    expect(await screen.findAllByRole('option')).toHaveLength(
      mockAPIResponse.length
    )

    await user.click(
      screen.getByText("17 Rue d'Entraigues 37000 Tours", { selector: 'span' })
    )

    expect(onAddressChosen).toHaveBeenCalledWith(mockAPIResponse[1])

    // Clear the input and tab to trigger the onBlur event
    await user.clear(input)
    await user.tab()

    expect(onAddressChosen).toHaveBeenCalledWith({
      address: '',
      city: '',
      id: '',
      latitude: '',
      longitude: '',
      label: '',
      postalCode: '',
      inseeCode: '',
    })
  })
})
