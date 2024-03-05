import { render, screen } from '@testing-library/react'
import { Form, Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { Contact } from '..'
import { SubmitButton } from '../../../../ui-kit'
import { DEFAULT_ACTIVITY_FORM_VALUES } from '../../Activity'
import informationsValidationSchema from '../../Activity/validationSchema'
import { VenueCreationFormValues } from '../../types'
import { ContactProps } from '../Contact'

const renderContact = ({
  initialValues,
  onSubmit = vi.fn(),
  props,
}: {
  initialValues: Partial<VenueCreationFormValues>
  onSubmit: () => void
  props: ContactProps
}) => {
  const validationSchema = yup.object().shape(informationsValidationSchema)

  render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={validationSchema}
    >
      <Form>
        <Contact {...props} />
        <SubmitButton isLoading={false}>Submit</SubmitButton>
      </Form>
    </Formik>
  )
}
describe('Contacts', () => {
  let props: ContactProps
  let initialValues: Partial<VenueCreationFormValues>
  const onSubmit = vi.fn()

  beforeEach(() => {
    initialValues = { ...DEFAULT_ACTIVITY_FORM_VALUES }
  })

  it('Should by default display contact section', () => {
    renderContact({ initialValues, onSubmit, props })

    expect(
      screen.getByText(
        'Cette adresse s’appliquera par défaut à toutes vos offres, vous pourrez la modifier à l’échelle de chaque offre.'
      )
    ).toBeInTheDocument()

    expect(screen.getByText('Contact')).toBeInTheDocument()
  })

  it('Should display less fields and infos when venue is virtual', () => {
    props = { isVenueVirtual: true }
    renderContact({ initialValues, onSubmit, props })

    expect(screen.queryByText('Contact')).not.toBeInTheDocument()

    expect(screen.getByLabelText(/Adresse email */)).toBeDisabled()

    expect(
      screen.queryByText(
        'Cette adresse s’appliquera par défaut à toutes vos offres, vous pourrez la modifier à l’échelle de chaque offre.'
      )
    ).not.toBeInTheDocument()
  })
})
