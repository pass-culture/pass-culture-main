import { render, screen } from '@testing-library/react'
import { Form, Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { VenueFormValues } from 'components/VenueForm/index'

import {
  validationSchema as withdrawalDetailsValidationSchema,
  WithdrawalDetails,
} from '../../WithdrawalDetails'

const renderWithdrawalDetails = ({
  initialValues,
  onSubmit = vi.fn(),
}: {
  isCreatedEntity: boolean
  initialValues: Partial<VenueFormValues>
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
  let initialValues: Partial<VenueFormValues>
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
