import { render, screen } from '@testing-library/react'
import { Form, Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { SubmitButton } from '../../../../ui-kit'
import { DEFAULT_ACTIVITY_FORM_VALUES } from '../../Activity'
import informationsValidationSchema from '../../Activity/validationSchema'
import { Contact } from '../../Contact'
import { IContactProps } from '../../Contact/Contact'
import { IVenueFormValues } from '../../types'

const renderContact = ({
  initialValues,
  onSubmit = jest.fn(),
  props,
}: {
  initialValues: Partial<IVenueFormValues>
  onSubmit: () => void
  props: IContactProps
}) => {
  const validationSchema = yup
    .object()
    .shape(informationsValidationSchema(false))

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
  let props: IContactProps
  let initialValues: Partial<IVenueFormValues>
  const onSubmit = jest.fn()

  beforeEach(() => {
    initialValues = { ...DEFAULT_ACTIVITY_FORM_VALUES }
  })

  it('Should by default display contact section', async () => {
    renderContact({ initialValues, onSubmit, props })

    expect(
      screen.getByText(
        'Cette adresse s’appliquera par défaut à toutes vos offres, vous pourrez la modifier à l’échelle de chaque offre.'
      )
    ).toBeInTheDocument()

    expect(screen.getByText('Contact')).toBeInTheDocument()
  })

  it('Should display less fields and infos when venue is virtual', async () => {
    props = { isVenueVirtual: true }
    renderContact({ initialValues, onSubmit, props })

    expect(screen.queryByText('Contact')).not.toBeInTheDocument()

    expect(screen.getByLabelText(/Adresse email/)).toBeDisabled()

    expect(
      screen.queryByText(
        'Cette adresse s’appliquera par défaut à toutes vos offres, vous pourrez la modifier à l’échelle de chaque offre.'
      )
    ).not.toBeInTheDocument()
  })
})
