import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import { IStockThingFormProps } from 'new_components/StockThingForm/StockThingForm'
import {
  EVENT_DATE_LABEL,
  EVENT_TIME_LABEL,
} from 'screens/OfferEducationalStock/constants/labels'
import { SubmitButton } from 'ui-kit'

import { STOCK_THING_EVENT_FORM_DEFAULT_VALUES } from '../constants'
import StockThingEventForm from '../StockThingEventForm'
import { getValidationSchemaArray } from '../validationSchema'
const today = new Date()
const yesterday = new Date(today.getDate() - 1)

const renderStockThingEventForm = ({
  minQuantity = null,
}: {
  minQuantity?: number | null
} = {}) => {
  const props: IStockThingFormProps = { today }
  return render(
    <Formik
      initialValues={STOCK_THING_EVENT_FORM_DEFAULT_VALUES}
      onSubmit={() => {}}
      validationSchema={getValidationSchemaArray(minQuantity)}
    >
      {({ handleSubmit }) => (
        <form onSubmit={handleSubmit}>
          <StockThingEventForm {...props} />
          <SubmitButton>Submit</SubmitButton>
        </form>
      )}
    </Formik>
  )
}

describe('StockThingEventForm:validationSchema', () => {
  it('test required fields', async () => {
    renderStockThingEventForm()

    await userEvent.click(screen.getByRole('button', { name: 'Submit' }))
    expect(screen.getByTestId('error-eventDatetime')).toBeInTheDocument()
    expect(screen.getByTestId('error-eventDate')).toBeInTheDocument()
    expect(screen.getByTestId('error-price')).toBeInTheDocument()
    expect(
      screen.queryByTestId('error-bookingLimitDatetime')
    ).not.toBeInTheDocument()
    expect(screen.queryByTestId('error-quantity')).not.toBeInTheDocument()
  })

  const dataSetEventDatetimeErrors = [
    { eventDatetime: '', error: 'Veuillez renseigner une date' },
    {
      eventDatetime: yesterday.getDate().toString(),
      error: "La date de l'évènement doit être supérieure à aujourd'hui",
    },
  ]
  it.each(dataSetEventDatetimeErrors)(
    'should display eventDatetime error',
    async ({ eventDatetime, error }) => {
      renderStockThingEventForm()

      const inputEventDatetime = screen.getByLabelText(EVENT_DATE_LABEL)
      await userEvent.type(inputEventDatetime, eventDatetime)
      await userEvent.tab()
      const errorPrice = screen.queryByTestId('error-eventDatetime')
      expect(errorPrice).toBeInTheDocument()
      expect(errorPrice).toHaveTextContent(error)
    }
  )

  // it('should not display eventDatetime error')

  const dataSetEventTimeErrors = [
    { eventTime: '', error: 'Veuillez renseigner un horaire' },
  ]
  it.each(dataSetEventTimeErrors)(
    'should display eventTime error',
    async ({ eventTime, error }) => {
      renderStockThingEventForm()

      const inputEventTime = screen.getByLabelText(EVENT_TIME_LABEL)
      await userEvent.type(inputEventTime, eventTime)
      await userEvent.tab()
      const errorPrice = screen.queryByTestId('error-eventTime')
      expect(errorPrice).toBeInTheDocument()
      expect(errorPrice).toHaveTextContent(error)
    }
  )

  // it('should not display eventTime error')

  const dataSetPriceErrors = [
    { price: '', error: 'Veuillez renseigner un prix' },
    {
      price: 'ABCD',
      error: 'Veuillez renseigner un prix',
    },
    {
      price: '-5',
      error: 'Le prix ne peut pas être inferieur à 0€',
    },
    {
      price: '301',
      error: 'Veuillez renseigner un prix inférieur à 300€',
    },
  ]
  it.each(dataSetPriceErrors)(
    'should display price error',
    async ({ price, error }) => {
      renderStockThingEventForm()

      const inputPrice = screen.getByLabelText('Prix')
      await userEvent.type(inputPrice, price)
      await userEvent.tab()
      const errorPrice = screen.queryByTestId('error-price')
      expect(errorPrice).toBeInTheDocument()
      expect(errorPrice).toHaveTextContent(error)
    }
  )

  const dataSetPrice = ['0', '100', '299']
  it.each(dataSetPrice)('should not display price error', async price => {
    renderStockThingEventForm()

    const inputPrice = screen.getByLabelText('Prix')
    await userEvent.type(inputPrice, price)
    await userEvent.tab()
    expect(screen.queryByTestId('error-price')).not.toBeInTheDocument()
  })

  const dataSetQuantityErrors = [
    {
      quantity: 'ABCD',
      error: 'Doit être un nombre',
    },
    {
      quantity: '-5',
      error: 'Doit être positif',
    },
  ]
  it.each(dataSetQuantityErrors)(
    'should display quantity error',
    async ({ quantity, error }) => {
      renderStockThingEventForm()

      const inputQuantity = screen.getByLabelText('Quantité')
      await userEvent.type(inputQuantity, quantity)
      await userEvent.tab()
      const errorquantity = screen.queryByTestId('error-quantity')
      expect(errorquantity).toBeInTheDocument()
      expect(errorquantity).toHaveTextContent(error)
    }
  )

  it('should display quantity error when min quantity is given', async () => {
    renderStockThingEventForm({ minQuantity: 10 })

    const inputQuantity = screen.getByLabelText('Quantité')
    await userEvent.type(inputQuantity, '9')
    await userEvent.tab()
    const errorquantity = screen.queryByTestId('error-quantity')
    expect(errorquantity).toBeInTheDocument()
    expect(errorquantity).toHaveTextContent('Quantité trop faible')
  })

  const dataSetquantity = ['0', '100', '350']
  it.each(dataSetquantity)(
    'should not display quantity error',
    async quantity => {
      renderStockThingEventForm()
      const inputQuantity = screen.getByLabelText('Quantité')
      await userEvent.type(inputQuantity, quantity)
      await userEvent.tab()
      expect(screen.queryByTestId('error-quantity')).not.toBeInTheDocument()
    }
  )

  // TODO: Test bookingLimitDatetime error when bookingLimitDatetime < eventDatetime
})
