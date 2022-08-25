import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { IVenueFormValues } from 'new_components/VenueForm'
import { SubmitButton } from 'ui-kit'

import { validationSchema as informationsValidationSchema } from '../'
import Informations, { IInformations } from '../Informations'

const renderInformations = async ({
  initialValues,
  onSubmit = jest.fn(),
  props,
}: {
  initialValues: Partial<IVenueFormValues>
  onSubmit: () => void
  props: IInformations
}) => {
  const validationSchema = yup.object().shape(informationsValidationSchema)
  const rtlReturns = await render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={validationSchema}
    >
      {({ handleSubmit }) => (
        <form onSubmit={handleSubmit}>
          <Informations {...props} />
          <SubmitButton isLoading={false}>Submit</SubmitButton>
        </form>
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

describe('components | Informations', () => {
  let props: IInformations
  let initialValues: Partial<IVenueFormValues>
  const onSubmit = jest.fn()

  beforeEach(() => {
    const updateIsSiretValued = jest.fn()
    initialValues = {}
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
    const { buttonSubmit } = await renderInformations({
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
    await renderInformations({
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
      'Choisissez un type de lieu dans la liste '
    )
    await userEvent.tab()
    expect(
      await screen.findByText('Veuillez sélectionner un type de lieu')
    ).toBeInTheDocument()
  })
})
