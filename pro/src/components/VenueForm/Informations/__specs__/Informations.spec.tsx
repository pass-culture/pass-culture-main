import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { apiAdresse } from 'apiClient/adresse'
import { api } from 'apiClient/api'
import { VenueFormValues } from 'components/VenueForm'
import { SubmitButton } from 'ui-kit'

import { DEFAULT_INFORMATIONS_FORM_VALUES } from '../constants'
import Informations, { InformationsProps } from '../Informations'
import generateSiretValidationSchema from '../SiretOrCommentFields/validationSchema'
import informationsValidationSchema from '../validationSchema'

const mockAdressData = [
  {
    address: '19 RUE LAITIERE',
    city: 'BAYEUX',
    id: '1',
    latitude: 11.1,
    longitude: -11.1,
    label: '19 RUE LAITIERE 14400 BAYEUX',
    postalCode: '14400',
  },
]

vi.mock('apiClient/adresse', () => {
  return {
    ...vi.importActual('apiClient/adresse'),
    default: {
      getDataFromAddress: vi.fn(),
    },
  }
})

const renderInformations = ({
  initialValues,
  onSubmit = vi.fn(),
  props,
}: {
  initialValues: Partial<VenueFormValues>
  onSubmit: () => void
  props: InformationsProps
}) => {
  const generateSiretOrCommentValidationSchema = generateSiretValidationSchema(
    '123456789',
    true
  )

  const validationSchema = generateSiretOrCommentValidationSchema.concat(
    yup.object().shape(informationsValidationSchema(false))
  )

  const rtlReturns = render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={validationSchema}
    >
      <Form>
        <Informations {...props} />
        <SubmitButton isLoading={false}>Submit</SubmitButton>
      </Form>
    </Formik>
  )

  return {
    ...rtlReturns,
    buttonSubmit: screen.getByRole('button', {
      name: 'Submit',
    }),
  }
}

describe('components | Informations', () => {
  let props: InformationsProps
  let initialValues: Partial<VenueFormValues>
  const onSubmit = vi.fn()

  beforeEach(() => {
    const updateIsSiretValued = vi.fn()
    const setIsSiretValued = vi.fn()
    initialValues = { ...DEFAULT_INFORMATIONS_FORM_VALUES }
    props = {
      isCreatedEntity: true,
      readOnly: false,
      updateIsSiretValued,
      setIsSiretValued,
      isVenueVirtual: false,
      siren: '123456789',
      isNewOnboardingActive: false,
    }
  })

  it('should submit form without errors', async () => {
    vi.spyOn(api, 'getSiretInfo').mockResolvedValueOnce({
      name: 'MUSEE DE LA TAPISSERIE DE BAYEUX',
      siret: '12345178912345',
      active: true,
      address: {
        street: '19 RUE LAITIERE',
        city: 'BAYEUX',
        postalCode: '14400',
      },
      ape_code: '95.07A',
      legal_category_code: '1000',
    })
    vi.spyOn(apiAdresse, 'getDataFromAddress').mockResolvedValue(mockAdressData)

    const { buttonSubmit } = renderInformations({
      initialValues,
      onSubmit,
      props,
    })
    const siretInput = screen.getByLabelText('SIRET du lieu', {
      exact: false,
    })

    await userEvent.type(siretInput, '12345678912345')
    await userEvent.tab()
    await userEvent.click(buttonSubmit)

    expect(onSubmit).toHaveBeenCalledTimes(1)
  })

  it('should validate required fields on submit', async () => {
    renderInformations({
      initialValues,
      onSubmit,
      props,
    })
    const nameInput = screen.getByText('Nom juridique')

    await userEvent.click(nameInput)
    await userEvent.tab()
    expect(
      await screen.findByText(
        'Veuillez renseigner le nom juridique de votre lieu'
      )
    ).toBeInTheDocument()
  })
})
