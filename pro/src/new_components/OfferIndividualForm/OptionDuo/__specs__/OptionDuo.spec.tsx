import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import { Form, Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm/types'
import { SubmitButton } from 'ui-kit'

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
        <SubmitButton isLoading={false}>Submit</SubmitButton>
      </Form>
    </Formik>
  )
}

describe('OfferIndividual section: OptionDuo', () => {
  const onSubmit = jest.fn()

  it('should render the component when "isDuo" option is available', async () => {
    const initialValues: Partial<IOfferIndividualFormValues> = {
      subCategoryFields: ['isDuo'],
    }
    await renderOptionDuo({
      initialValues,
      onSubmit,
    })
    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Réservations “duo“' })
      ).toBeInTheDocument()

      expect(
        screen.getByLabelText('Accepter les réservations “duo“', {
          exact: false,
        })
      ).toBeInTheDocument()
    })
  })

  it('should not render the component when "isDuo" option not available', async () => {
    const initialValues: Partial<IOfferIndividualFormValues> = {
      subCategoryFields: [],
    }
    await renderOptionDuo({
      initialValues,
      onSubmit,
    })
    await waitFor(() => {
      expect(
        screen.queryByRole('heading', { name: 'Réservations “duo“' })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByLabelText('Accepter les réservations "duo"', {
          exact: false,
        })
      ).not.toBeInTheDocument()
    })
  })
})
