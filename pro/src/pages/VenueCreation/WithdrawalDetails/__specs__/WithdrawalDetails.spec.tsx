import { render, screen } from '@testing-library/react'
import { Form, Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { VenueSettingsFormValues } from 'pages/VenueSettings/types'

import {
  validationSchema as withdrawalDetailsValidationSchema,
  WithdrawalDetails,
} from '..'

const renderWithdrawalDetails = ({
  initialValues,
  onSubmit = vi.fn(),
}: {
  isCreatedEntity: boolean
  initialValues: Partial<VenueSettingsFormValues>
  onSubmit: () => void
}) => {
  const validationSchema = yup.object().shape(withdrawalDetailsValidationSchema)
  render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={validationSchema}
    >
      {({ handleSubmit }) => (
        <Form onSubmit={handleSubmit}>
          <WithdrawalDetails />
        </Form>
      )}
    </Formik>
  )
}

describe('components | WithdrawalDetails', () => {
  let initialValues: Partial<VenueSettingsFormValues>
  const onSubmit = vi.fn()

  it('should display checkbox', async () => {
    initialValues = {
      withdrawalDetails: 'Tototata',
      isWithdrawalAppliedOnAllOffers: false,
    }
    renderWithdrawalDetails({
      isCreatedEntity: false,
      initialValues,
      onSubmit,
    })

    expect(
      await screen.findByLabelText(/Appliquer le changement/)
    ).toBeInTheDocument()
  })
})
