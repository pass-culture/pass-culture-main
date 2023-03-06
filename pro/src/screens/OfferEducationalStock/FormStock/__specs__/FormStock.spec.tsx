import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'

import {
  EducationalOfferType,
  Mode,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import { validationSchema } from 'screens/OfferEducationalStock/validationSchema'
import { SubmitButton } from 'ui-kit'

import FormStock, { IFormStockProps } from '../FormStock'

const renderFormStock = ({
  initialValues,
  onSubmit = jest.fn(),
  props,
}: {
  initialValues: OfferEducationalStockFormValues
  onSubmit: () => void
  props: IFormStockProps
}) => {
  return render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={validationSchema}
    >
      <Form>
        <FormStock {...props} />
        <SubmitButton isLoading={false}>Enregistrer</SubmitButton>
      </Form>
    </Formik>
  )
}

describe('TimePicker', () => {
  let initialValues: OfferEducationalStockFormValues
  const onSubmit = jest.fn()
  let props: IFormStockProps

  beforeEach(() => {
    props = {
      mode: Mode.CREATION,
      disablePriceAndParticipantInputs: false,
      preventPriceIncrease: false,
    }
    initialValues = {
      eventDate: '',
      eventTime: '',
      numberOfPlaces: '',
      totalPrice: '',
      bookingLimitDatetime: null,
      priceDetail: '',
      educationalOfferType: EducationalOfferType.SHOWCASE,
    }
  })

  it('should display an error when the field is empty', async () => {
    renderFormStock({ initialValues: initialValues, onSubmit, props })

    const saveButton = screen.getByText('Enregistrer')

    await userEvent.click(saveButton)
    const requiredField = screen.getAllByText('Champ requis')
    expect(requiredField).toHaveLength(4)
  })

  it('should automatically update bookingLimitDatetime when the user edits the event date', async () => {
    renderFormStock({
      initialValues: { ...initialValues, eventDate: new Date() },
      onSubmit,
      props: {
        mode: Mode.EDITION,
        disablePriceAndParticipantInputs: false,
        preventPriceIncrease: false,
      },
    })

    const dateInput = screen.getByLabelText('Date')
    await userEvent.click(dateInput)
    await userEvent.clear(dateInput)
    await waitFor(() => userEvent.type(dateInput, '10/05/2023'))
    const bookingLimitDatetimeInput = screen.getByLabelText(
      'Date limite de réservation'
    )
    expect(bookingLimitDatetimeInput).toHaveValue('10/05/2023')
  })

  it('should not disable price and place when offer status is reimbursment', async () => {
    renderFormStock({
      initialValues: initialValues,
      onSubmit,
      props: {
        mode: Mode.READ_ONLY,
        disablePriceAndParticipantInputs: true,
        preventPriceIncrease: true,
      },
    })

    const priceInput = screen.getByLabelText('Prix global TTC')
    const placeInput = screen.getByLabelText('Nombre de places')

    expect(priceInput).toBeDisabled()
    expect(placeInput).toBeDisabled()
  })

  it('should not allow price to be greater than initial value', async () => {
    renderFormStock({
      initialValues: { ...initialValues, totalPrice: 1000 },
      onSubmit,
      props: {
        mode: Mode.READ_ONLY,
        disablePriceAndParticipantInputs: false,
        preventPriceIncrease: true,
      },
    })

    const priceInput = screen.getByLabelText('Prix global TTC')
    await userEvent.clear(priceInput)
    await userEvent.type(priceInput, '10000')

    expect(priceInput).toBeInvalid()
  })
})
