import { yupResolver } from '@hookform/resolvers/yup'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { FormEvent } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { vi } from 'vitest'

import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import {
  getIndividualOfferFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { MOCKED_SUBCATEGORY } from '@/pages/IndividualOffer/commons/__mocks__/constants'

import { getInitialValuesFromOffer } from '../../../commons/utils/getInitialValuesFromOffer'
import { getValidationSchema } from '../../../commons/utils/getValidationSchema'
import { AddressManualAdapter } from './AddressManualAdapter'

vi.mock('@/ui-kit/form/AddressSelect/AddressSelect', () => ({
  AddressSelect: ({
    label,
    disabled,
  }: {
    label: string
    disabled?: boolean
  }) => <input aria-label={label} role="combobox" disabled={disabled} />,
}))

beforeAll(() => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue({
    ok: true,
    json: async () => ({}),
  } as unknown as Response)
  vi.spyOn(console, 'error').mockImplementation(() => {})
  vi.spyOn(console, 'warn').mockImplementation(() => {})
})

const renderAddressManualAdapter = ({
  offer,
}: {
  offer: GetIndividualOfferWithAddressResponseModel
}) => {
  const Harness = () => {
    const validationSchema = getValidationSchema({
      isDigital: false,
    })
    const initialValues = getInitialValuesFromOffer(offer, {
      offerVenue: makeVenueListItem({ id: 2 }),
    })
    const form = useForm({
      defaultValues: initialValues,
      mode: 'all',
      resolver: yupResolver(validationSchema),
    })

    const onSubmit = (event: FormEvent) => {
      // Prevent `Error: Not implemented: HTMLFormElement.prototype.requestSubmit` error
      // https://stackoverflow.com/a/62404526/2736233
      event.preventDefault()

      form.handleSubmit(vi.fn())()
    }

    return (
      <FormProvider {...form}>
        <form onSubmit={onSubmit}>
          <AddressManualAdapter />

          <div data-testid="address.street">{form.watch('address.street')}</div>
          <div data-testid="address.postalCode">
            {form.watch('address.postalCode')}
          </div>
          <div data-testid="address.city">{form.watch('address.city')}</div>
          <div data-testid="address.coords">{form.watch('address.coords')}</div>
          <div data-testid="address.latitude">
            {form.watch('address.latitude')}
          </div>
          <div data-testid="address.longitude">
            {form.watch('address.longitude')}
          </div>

          <button type="submit">Submit Test Form</button>
        </form>
      </FormProvider>
    )
  }

  return renderWithProviders(<Harness />)
}

const LABELS = {
  fields: {
    street: /Adresse postale/,
    postalCode: /Code postal/,
    city: /Ville/,
    coords: /Coordonnées GPS/,
  },
}

describe('AddressManualAdapter', () => {
  const offerBase = getIndividualOfferFactory({
    id: 1,
    address: {
      id: 2,
      id_oa: 3,
      street: '12 rue du Test',
      postalCode: '34567',
      city: 'Test-sur-Seine',
      latitude: 1.23,
      longitude: 4.56,
      isManualEdition: true,
    },
    subcategoryId: MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE.id,
  })

  it('should render the form fields', () => {
    renderAddressManualAdapter({ offer: offerBase })

    expect(screen.getByLabelText(LABELS.fields.street)).toHaveValue(
      '12 rue du Test'
    )
    expect(screen.getByLabelText(LABELS.fields.postalCode)).toHaveValue('34567')
    expect(screen.getByLabelText(LABELS.fields.city)).toHaveValue(
      'Test-sur-Seine'
    )
    expect(screen.getByLabelText(LABELS.fields.coords)).toHaveValue(
      '1.23, 4.56'
    )
  })

  it('should sync manual input fields to nested parent values (street, postal code)', async () => {
    renderAddressManualAdapter({ offer: offerBase })

    const streetInput = screen.getByLabelText(LABELS.fields.street)
    await userEvent.clear(streetInput)
    await userEvent.type(streetInput, '34 Boulevard du Test')

    expect(screen.getByTestId('address.street')).toHaveTextContent(
      '34 Boulevard du Test'
    )

    const postalCodeInput = screen.getByLabelText(LABELS.fields.postalCode)
    await userEvent.clear(postalCodeInput)
    await userEvent.type(postalCodeInput, '89012')

    expect(screen.getByTestId('address.postalCode')).toHaveTextContent('89012')

    const cityInput = screen.getByLabelText(LABELS.fields.city)
    await userEvent.clear(cityInput)
    await userEvent.type(cityInput, 'Test-sur-Mer')

    expect(screen.getByTestId('address.city')).toHaveTextContent('Test-sur-Mer')

    const coordsInput = screen.getByLabelText(LABELS.fields.coords)
    await userEvent.clear(coordsInput)
    // We [TAB] to trigger the onBlur event that parses and sets latitude and longitude in `AddressManual`.
    await userEvent.type(coordsInput, '7.89, 0.12[TAB]')

    expect(screen.getByTestId('address.latitude')).toHaveTextContent('7.89')
    expect(screen.getByTestId('address.longitude')).toHaveTextContent('0.12')
  })

  // This test requires some beforehand typing to trigger form state updates on clear
  // Maybe because of https://github.com/testing-library/user-event/discussions/970.
  it.each([
    ['street', 'Veuillez renseigner une adresse postale'],
    ['postalCode', 'Veuillez renseigner un code postal valide'],
    ['city', 'Veuillez renseigner une ville'],
    ['coords', 'Veuillez renseigner les coordonnées GPS'],
  ])('should pass main Locaion form validation errors down to AddressManual subform field (%s)', async (field, expectedErrorMessage) => {
    renderAddressManualAdapter({ offer: offerBase })

    const input = screen.getByLabelText(
      LABELS.fields[field as keyof typeof LABELS.fields]
    )
    await userEvent.type(input, ' ')
    await userEvent.clear(input)

    expect(screen.getByTestId(`address.${field}`)).toBeEmptyDOMElement()

    await userEvent.click(
      screen.getByRole('button', { name: 'Submit Test Form' })
    )

    expect(await screen.findByText(expectedErrorMessage)).toBeInTheDocument()
  })
})
