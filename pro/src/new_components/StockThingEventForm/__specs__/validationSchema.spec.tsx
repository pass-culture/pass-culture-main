import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import { IStockThingFormProps } from 'new_components/StockThingForm/StockThingForm'
import { SubmitButton } from 'ui-kit'
import { getToday } from 'utils/date'

import { STOCK_THING_EVENT_FORM_DEFAULT_VALUES } from '../constants'
import StockThingEventForm from '../StockThingEventForm'
import { getValidationSchema } from '../validationSchema'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2022-12-25T00:00:00Z')),
}))

const today = getToday()
const yesterday = getToday()
const tomorrow = getToday()
yesterday.setDate(yesterday.getDate() - 1)
tomorrow.setDate(tomorrow.getDate() + 1)

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
      validationSchema={getValidationSchema(minQuantity)}
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
    expect(screen.getByTestId('error-eventTime')).toBeInTheDocument()
    expect(screen.getByTestId('error-price')).toBeInTheDocument()
    expect(
      screen.queryByTestId('error-bookingLimitDatetime')
    ).not.toBeInTheDocument()
    expect(screen.queryByTestId('error-quantity')).not.toBeInTheDocument()
  })

  const dataSetEventDatetimeErrors = [
    {
      eventDatetime: yesterday.getDate().toString(),
      error: "La date de l'évènement doit être supérieure à aujourd'hui",
    },
  ]
  it.each(dataSetEventDatetimeErrors)(
    'should display eventDatetime error',
    async ({ eventDatetime, error }) => {
      renderStockThingEventForm()

      await userEvent.click(screen.getAllByPlaceholderText('JJ/MM/AAAA')[0])
      await userEvent.click(screen.getByText(eventDatetime))
      const errorEventDatetime = screen.queryByTestId('error-eventDatetime')
      expect(errorEventDatetime).toBeInTheDocument()
      expect(errorEventDatetime).toHaveTextContent(error)
    }
  )

  const dataSetEventDateTime: Array<number> = [
    today.getDate(),
    tomorrow.getDate(),
  ]
  it.each(dataSetEventDateTime)(
    'should not display eventDatetime error',
    async eventDateTime => {
      renderStockThingEventForm()

      await userEvent.click(screen.getAllByPlaceholderText('JJ/MM/AAAA')[0])
      await userEvent.click(screen.getByText(eventDateTime))
      const errorEventDatetime = screen.queryByTestId('error-eventDatetime')
      expect(errorEventDatetime).not.toBeInTheDocument()
    }
  )

  const dataSetPriceErrors = [
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

  it('should display bookingLimitDatetime error when bookingLimitDatetime > eventDatetime', async () => {
    renderStockThingEventForm()

    const todayNumber = today.getDate().toString()
    await userEvent.click(screen.getAllByPlaceholderText('JJ/MM/AAAA')[0])
    await userEvent.click(screen.getByText(todayNumber))

    const errorEventDatetime = screen.queryByTestId('error-eventDatetime')
    expect(errorEventDatetime).not.toBeInTheDocument()

    await userEvent.click(screen.getAllByPlaceholderText('JJ/MM/AAAA')[1])
    await userEvent.click(screen.getByText(tomorrow.getDate().toString()))

    const errorBookingLimitDatetime = screen.queryByTestId(
      'error-bookingLimitDatetime'
    )
    expect(errorBookingLimitDatetime).toBeInTheDocument()
    expect(errorBookingLimitDatetime).toHaveTextContent(
      "Veuillez rentrer une date antérieur à la date de l'évènement"
    )
  })

  const dataSetBookingLimitDatetimeError = [
    {
      eventDateTime: today.getDate(),
      bookingLimitDatetime: yesterday.getDate(),
    },
    {
      eventDateTime: tomorrow.getDate(),
      bookingLimitDatetime: tomorrow.getDate(),
    },
  ]
  it.each(dataSetBookingLimitDatetimeError)(
    'should not display bookingLimitDatetime error when datetime strictly before eventDatetime',
    async ({ eventDateTime, bookingLimitDatetime }) => {
      renderStockThingEventForm()

      await userEvent.click(screen.getAllByPlaceholderText('JJ/MM/AAAA')[0])
      await userEvent.click(screen.getByText(eventDateTime))
      const errorEventDatetime = screen.queryByTestId('error-eventDatetime')
      expect(errorEventDatetime).not.toBeInTheDocument()

      await userEvent.click(screen.getAllByPlaceholderText('JJ/MM/AAAA')[1])
      await userEvent.click(screen.getByText(bookingLimitDatetime))

      const errorBookingLimitDatetime = screen.queryByTestId(
        'error-bookingLimitDatetime'
      )
      expect(errorBookingLimitDatetime).not.toBeInTheDocument()
    }
  )
})
