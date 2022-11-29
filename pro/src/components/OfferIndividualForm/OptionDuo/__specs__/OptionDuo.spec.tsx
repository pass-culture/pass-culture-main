import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { IOfferIndividualFormValues } from 'components/OfferIndividualForm/types'

import OptionDuo, { IOptionDuo } from '../OptionDuo'
import validationSchema from '../validationSchema'

const renderOptionDuo = ({
  props,
  initialValues,
  onSubmit = jest.fn(),
}: {
  props?: IOptionDuo
  initialValues: Partial<IOfferIndividualFormValues>
  onSubmit: () => void
}) => {
  return render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      <OptionDuo {...props} />
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

  it('should disable read only fields', () => {
    const initialValues: Partial<IOfferIndividualFormValues> = {
      subCategoryFields: ['isDuo'],
    }
    const props = {
      readOnlyFields: ['isDuo'],
    }

    renderOptionDuo({
      props,
      initialValues,
      onSubmit,
    })

    expect(screen.getByTestId('checkbox')).toBeDisabled()
  })
})
