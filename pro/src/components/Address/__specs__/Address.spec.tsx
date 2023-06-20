import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { apiAdresse } from 'apiClient/adresse'
import { VenueFormValues } from 'components/VenueForm'
import { SubmitButton } from 'ui-kit'

import { Address, validationSchema as addressValidationSchema } from '../'

const mockAdressData = [
  {
    address: '12 rue des lilas',
    city: 'Lyon',
    id: '1',
    latitude: 11.1,
    longitude: -11.1,
    label: '12 rue des lilas 69002 Lyon',
    postalCode: '69002',
  },
  {
    address: '12 rue des tournesols',
    city: 'Paris',
    id: '2',
    latitude: 22.2,
    longitude: -2.22,
    label: '12 rue des tournesols 75003 Paris',
    postalCode: '75003',
  },
]

jest.mock('apiClient/adresse', () => {
  return {
    ...jest.requireActual('apiClient/adresse'),
    default: {
      getDataFromAddress: jest.fn(),
    },
  }
})

const renderAddress = async ({
  initialValues,
  onSubmit = jest.fn(),
}: {
  initialValues: Partial<VenueFormValues>
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
          <Address />
          <SubmitButton isLoading={false}>Submit</SubmitButton>
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

describe('components | Address', () => {
  let initialValues: Partial<VenueFormValues>
  const onSubmit = jest.fn()

  beforeEach(() => {
    initialValues = {
      address: '',
      addressAutocomplete: '',
      'search-addressAutocomplete': '',
      city: '',
      postalCode: '',
      latitude: 0,
      longitude: 0,
    }
    jest
      .spyOn(apiAdresse, 'getDataFromAddress')
      .mockResolvedValue(mockAdressData)
  })

  it('should submit form without errors', async () => {
    const { buttonSubmit } = await renderAddress({
      initialValues,
      onSubmit,
    })
    const adressInput = screen.getByLabelText('Adresse postale')

    await userEvent.type(adressInput, '12 rue ')
    const suggestion = await screen.getByText(
      '12 rue des tournesols 75003 Paris',
      { selector: 'span' }
    )

    await userEvent.click(suggestion)
    await userEvent.click(buttonSubmit)

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        {
          address: '12 rue des tournesols',
          addressAutocomplete: '12 rue des tournesols 75003 Paris',
          city: 'Paris',
          latitude: 22.2,
          longitude: -2.22,
          postalCode: '75003',
          'search-addressAutocomplete': '12 rue des tournesols 75003 Paris',
        },
        expect.anything()
      )
    })
  })

  it('should not display suggestions when api return an error', async () => {
    jest
      .spyOn(apiAdresse, 'getDataFromAddress')
      .mockRejectedValue('Erreur lors de la récupération des données')
    await renderAddress({
      initialValues,
      onSubmit,
    })
    const adressInput = screen.getByLabelText('Adresse postale')

    await userEvent.type(adressInput, '12 rue')
    expect(
      screen.queryByText('12 rue des tournesols 75003 Paris')
    ).not.toBeInTheDocument()
  })
})
