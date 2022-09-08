import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import { Formik } from 'formik'
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
      <OptionDuo />
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
    expect(
      screen.getByRole('heading', { name: 'Réservations “Duo“' })
    ).toBeInTheDocument()

    expect(
      screen.getByLabelText('Accepter les réservations “duo“', {
        exact: false,
      })
    ).toBeInTheDocument()
  })

  it('should not render the component when "isDuo" option not available', async () => {
    const initialValues: Partial<IOfferIndividualFormValues> = {
      subCategoryFields: [],
    }
    await renderOptionDuo({
      initialValues,
      onSubmit,
    })
    expect(
      screen.queryByRole('heading', { name: 'Réservations “Duo“' })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Accepter les réservations "duo"', {
        exact: false,
      })
    ).not.toBeInTheDocument()
  })
})
