import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { IVenueFormValues } from 'new_components/VenueForm'
import { SubmitButton } from 'ui-kit'

import Activity, { IActivity } from '../Activity'
import { DEFAULT_ACTIVITY_FORM_VALUES } from '../constants'
import informationsValidationSchema from '../validationSchema'

const renderInformations = ({
  initialValues,
  onSubmit = jest.fn(),
  props,
}: {
  initialValues: Partial<IVenueFormValues>
  onSubmit: () => void
  props: IActivity
}) => {
  const validationSchema = yup.object().shape(informationsValidationSchema)

  render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={validationSchema}
    >
      <Form>
        <Activity {...props} />
        <SubmitButton isLoading={false}>Submit</SubmitButton>
      </Form>
    </Formik>
  )
}

describe('components | Activity', () => {
  let props: IActivity
  let initialValues: Partial<IVenueFormValues>
  const onSubmit = jest.fn()

  beforeEach(() => {
    initialValues = { ...DEFAULT_ACTIVITY_FORM_VALUES }
    props = {
      venueLabels: [],
      venueTypes: [{ value: 'CINEMA', label: 'Cinéma, salle de projection' }],
    }
  })

  it('should submit form without errors', async () => {
    renderInformations({
      initialValues,
      onSubmit,
      props,
    })
    const buttonSubmit = screen.getByRole('button', {
      name: 'Submit',
    })
    const venueTypeSelect = screen.getByLabelText('Type de lieu')
    await userEvent.selectOptions(venueTypeSelect, 'CINEMA')
    await userEvent.click(buttonSubmit)
    expect(onSubmit).toHaveBeenCalledTimes(1)
  })

  it('should validate required fields on submit', async () => {
    renderInformations({
      initialValues,
      onSubmit,
      props,
    })
    const venueTypeSelect = screen.getByLabelText('Type de lieu')
    await userEvent.selectOptions(
      venueTypeSelect,
      'Sélectionner celui qui correspond à votre lieu'
    )
    await userEvent.tab()
    expect(
      screen.getByText('Veuillez sélectionner un type de lieu')
    ).toBeInTheDocument()
  })
})
