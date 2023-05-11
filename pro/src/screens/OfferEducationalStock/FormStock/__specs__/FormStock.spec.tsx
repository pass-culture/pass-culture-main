import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'
import { Form, Formik } from 'formik'
import React from 'react'

import {
  EducationalOfferType,
  Mode,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import { generateValidationSchema } from 'screens/OfferEducationalStock/validationSchema'
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
      validationSchema={generateValidationSchema(
        props.preventPriceIncrease,
        initialValues.totalPrice
      )}
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
      offerDateCreated: '2023-04-06T13:48:36.304896Z',
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
    const requiredField = await screen.findAllByText('Champ requis')
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
        offerDateCreated: '2023-04-06T13:48:36.304896Z',
      },
    })
    const userDateInput = addDays(new Date(), 1).toLocaleDateString('fr-FR')
    const dateInput = screen.getByLabelText('Date')
    await userEvent.click(dateInput)
    await userEvent.clear(dateInput)
    await waitFor(() => userEvent.type(dateInput, userDateInput))
    const bookingLimitDatetimeInput = screen.getByLabelText(
      'Date limite de réservation'
    )
    expect(bookingLimitDatetimeInput).toHaveValue(userDateInput)
  })

  it('should not disable price and place when offer status is reimbursment', async () => {
    renderFormStock({
      initialValues: initialValues,
      onSubmit,
      props: {
        mode: Mode.READ_ONLY,
        disablePriceAndParticipantInputs: true,
        preventPriceIncrease: true,
        offerDateCreated: '2023-04-06T13:48:36.304896Z',
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
        offerDateCreated: '2023-04-06T13:48:36.304896Z',
      },
    })

    const priceInput = screen.getByLabelText('Prix global TTC')
    await userEvent.clear(priceInput)
    await userEvent.type(priceInput, '10000')
    const saveButton = screen.getByText('Enregistrer')

    await userEvent.click(saveButton)

    expect(priceInput).toBeInvalid()
    expect(
      screen.getByText('Vous ne pouvez pas définir un prix plus élevé.')
    ).toBeInTheDocument()
  })
})
