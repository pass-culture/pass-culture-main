import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik, Form } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm/types'

import OptionDuo from '../OptionDuo'
import validationSchema from '../validationSchema'

const renderOptionDuo = ({
  initialValues,
  onSubmit = jest.fn(),
}: {
  initialValues: Partial<IOfferIndividualFormValues>
  onSubmit: () => void
}) => {
  return render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      <Form>
        <OptionDuo />
        <button type="submit">Submit</button>
      </Form>
    </Formik>
  )
}

describe('OfferIndividual section: OptionDuo', () => {
  const onSubmit = jest.fn()

  it('onSubmit call should include "isDuo" value', async () => {
    const initialValues: Partial<IOfferIndividualFormValues> = {
      subCategoryFields: ['isDuo'],
    }
    await renderOptionDuo({
      initialValues,
      onSubmit,
    })
    await userEvent.click(
      screen.getByLabelText('Accepter les réservations “duo“', {
        exact: false,
      })
    )
    await userEvent.click(screen.getByRole('button', { name: 'Submit' }))
    expect(onSubmit).toHaveBeenCalledWith(
      {
        isDuo: true,
        subCategoryFields: ['isDuo'],
      },
      expect.anything()
    )
    expect(screen.queryByTestId('error-isDuo')).not.toBeInTheDocument()
  })
})
