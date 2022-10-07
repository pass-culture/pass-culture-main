import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { IVenueFormValues } from 'new_components/VenueForm'
import { SubmitButton } from 'ui-kit'

import {
  DEFAULT_INFORMATIONS_FORM_VALUES,
  validationSchema as informationsValidationSchema,
} from '../'
import Informations, { IInformations } from '../Informations'

const renderInformations = ({
  initialValues,
  onSubmit = jest.fn(),
  props,
}: {
  initialValues: Partial<IVenueFormValues>
  onSubmit: () => void
  props: IInformations
}) => {
  const validationSchema = yup.object().shape(informationsValidationSchema)
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
  let props: IInformations
  let initialValues: Partial<IVenueFormValues>
  const onSubmit = jest.fn()

  beforeEach(() => {
    const updateIsSiretValued = jest.fn()
    initialValues = { ...DEFAULT_INFORMATIONS_FORM_VALUES }
    props = {
      isCreatedEntity: true,
      readOnly: false,
      updateIsSiretValued,
      venueIsVirtual: false,
      venueLabels: [],
      venueTypes: [{ value: 'CINEMA', label: 'Cinéma, salle de projection' }],
    }
  })

  it('should submit form without errors', async () => {
    const { buttonSubmit } = renderInformations({
      initialValues,
      onSubmit,
      props,
    })
    const nameInput = screen.getByLabelText('Nom du lieu', {
      exact: false,
    })
    const mailInput = screen.getByLabelText('Mail', {
      exact: false,
    })
    const venueTypeSelect = screen.getByLabelText('Type de lieu', {
      exact: false,
    })

    await userEvent.type(nameInput, 'Mon super cinéma')
    await userEvent.type(mailInput, 'superCine@example.com')
    await userEvent.selectOptions(venueTypeSelect, 'CINEMA')

    await userEvent.click(buttonSubmit)

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledTimes(1)
    })
  })

  it('should validate required fields on submit', async () => {
    renderInformations({
      initialValues,
      onSubmit,
      props,
    })
    const nameInput = screen.getByLabelText('Nom du lieu', {
      exact: false,
    })
    const mailInput = screen.getByLabelText('Mail', {
      exact: false,
    })
    const venueTypeSelect = screen.getByLabelText('Type de lieu', {
      exact: false,
    })

    await userEvent.click(nameInput)
    await userEvent.tab()
    expect(
      await screen.findByText('Veuillez renseigner un nom')
    ).toBeInTheDocument()

    await userEvent.click(mailInput)
    await userEvent.tab()
    expect(
      await screen.findByText('Veuillez renseigner une adresse email')
    ).toBeInTheDocument()

    await userEvent.selectOptions(
      venueTypeSelect,
      'Sélectionner celui qui correspond à votre lieu'
    )
    await userEvent.tab()
    expect(
      await screen.findByText('Veuillez sélectionner un type de lieu')
    ).toBeInTheDocument()
  })
})
