import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik, Form } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'

import { OPTION_DUO_DEFAULT_VALUES } from '..'
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
  let initialValues: Partial<IOfferIndividualFormValues>

  beforeEach(() => {
    initialValues = {
      subCategoryFields: ['isDuo'],
      ...OPTION_DUO_DEFAULT_VALUES,
    }
  })

  it('onSubmit call should include "isDuo" default', async () => {
    await renderOptionDuo({
      initialValues,
      onSubmit,
    })

    await userEvent.click(screen.getByRole('button', { name: 'Submit' }))

    await waitFor(() => {
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

  it('should submit clicked isDuo value', async () => {
    await renderOptionDuo({
      initialValues,
      onSubmit,
    })

    const isDuoOption = await screen.getByLabelText(
      'Accepter les réservations “duo“',
      {
        exact: false,
      }
    )
    await userEvent.click(isDuoOption)

    await userEvent.click(await screen.findByText('Submit'))

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        { isDuo: false, subCategoryFields: ['isDuo'] },
        expect.anything()
      )
    })
  })

  it('should not submit isDuo when option is not available', async () => {
    initialValues.subCategoryFields = []

    await renderOptionDuo({
      initialValues,
      onSubmit,
    })

    await userEvent.click(await screen.findByText('Submit'))
    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        {
          isDuo: true,
          subCategoryFields: [],
        },
        expect.anything()
      )
    })
  })
})
