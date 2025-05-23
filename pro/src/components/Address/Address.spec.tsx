import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import * as yup from 'yup'

import * as apiAdresse from 'apiClient/adresse/apiAdresse'
import { VenueSettingsFormValues } from 'pages/VenueSettings/types'
import { Button } from 'ui-kit/Button/Button'

import { AddressSelect } from './Address'
import { validationSchema as addressValidationSchema } from './validationSchema'

const mockAdressData = [
  {
    address: '12 rue des lilas',
    city: 'Lyon',
    id: '1',
    latitude: 11.1,
    longitude: -11.1,
    label: '12 rue des lilas 69002 Lyon',
    postalCode: '69002',
    inseeCode: '69382',
  },
  {
    address: '12 rue des tournesols',
    city: 'Paris',
    id: '2',
    latitude: 22.2,
    longitude: -2.22,
    label: '12 rue des tournesols 75003 Paris',
    postalCode: '75003',
    inseeCode: '75103',
  },
]

vi.mock('apiClient/adresse', async () => {
  return {
    ...(await vi.importActual('apiClient/adresse/apiAdresse')),
    default: {
      getDataFromAddress: vi.fn(),
    },
  }
})

const renderAddress = ({
  initialValues,
  onSubmit = vi.fn(),
}: {
  initialValues: Partial<VenueSettingsFormValues>
  onSubmit: () => void
}) => {
  const validationSchema = yup.object().shape(addressValidationSchema)
  const rtlReturns = render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={validationSchema}
    >
      {({ handleSubmit }) => (
        <Form onSubmit={handleSubmit}>
          <AddressSelect />
          <Button type="submit" isLoading={false}>
            Submit
          </Button>
        </Form>
      )}
    </Formik>
  )

  return {
    ...rtlReturns,
    buttonSubmit: screen.getByRole('button', {
      name: 'Submit',
    }),
  }
}

describe('AddressSelect', () => {
  let initialValues: Partial<VenueSettingsFormValues>
  const onSubmit = vi.fn()

  beforeEach(() => {
    initialValues = {
      addressAutocomplete: '',
      'search-addressAutocomplete': '',
      city: '',
      postalCode: '',
      latitude: '',
      longitude: '',
      street: '',
    }
    vi.spyOn(apiAdresse, 'getDataFromAddress').mockResolvedValue(mockAdressData)
  })

  it('should submit form without errors', async () => {
    const { buttonSubmit } = renderAddress({ initialValues, onSubmit })
    const adressInput = screen.getByLabelText('Adresse postale *')

    await userEvent.type(adressInput, '12 rue ')

    const suggestion = await screen.findByText(
      '12 rue des tournesols 75003 Paris',
      {
        selector: 'span',
      }
    )

    await userEvent.click(suggestion)
    await userEvent.click(buttonSubmit)

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        {
          addressAutocomplete: '12 rue des tournesols 75003 Paris',
          city: 'Paris',
          banId: '2',
          latitude: 22.2,
          longitude: -2.22,
          postalCode: '75003',
          inseeCode: '75103',
          'search-addressAutocomplete': '12 rue des tournesols 75003 Paris',
          street: '12 rue des tournesols',
        },
        expect.anything()
      )
    })
  })

  it('should not display suggestions when api return an error', async () => {
    vi.spyOn(apiAdresse, 'getDataFromAddress').mockRejectedValue(
      'Erreur lors de la récupération des données'
    )
    renderAddress({ initialValues, onSubmit })
    const adressInput = screen.getByLabelText('Adresse postale *')

    await userEvent.type(adressInput, '12 rue')
    expect(
      screen.queryByText('12 rue des tournesols 75003 Paris')
    ).not.toBeInTheDocument()
  })
})
