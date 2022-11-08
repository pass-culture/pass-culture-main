import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { format as formatDate } from 'date-fns'
import { Formik } from 'formik'
import React from 'react'

import { SubmitButton } from 'ui-kit'
import { getToday } from 'utils/date'

import { STOCK_EVENT_FORM_DEFAULT_VALUES } from '../constants'
import StockEventForm, { IStockEventFormProps } from '../StockEventForm'
import { getValidationSchema } from '../validationSchema'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2022-12-15T00:00:00Z')),
}))

const today = getToday()
const tomorrow = getToday()
const yesterday = getToday()
const oneWeekLater = getToday()
tomorrow.setDate(tomorrow.getDate() + 1)
yesterday.setDate(yesterday.getDate() - 1)
oneWeekLater.setDate(oneWeekLater.getDate() + 7)

const renderStockEventForm = ({
  minQuantity,
  onSubmit = jest.fn(),
}: {
  minQuantity?: number | null
  onSubmit?: () => void
} = {}) => {
  const props: IStockEventFormProps = { today, fieldPrefix: 'stocks[0]' }
  return render(
    <Formik
      initialValues={{
        stocks: [STOCK_EVENT_FORM_DEFAULT_VALUES],
      }}
      onSubmit={onSubmit}
      validationSchema={getValidationSchema(minQuantity)}
    >
      {({ handleSubmit }) => (
        <form onSubmit={handleSubmit}>
          <StockEventForm {...props} />
          <SubmitButton>Submit</SubmitButton>
        </form>
      )}
    </Formik>
  )
}

describe('StockEventForm:validationSchema', () => {
  it('test required fields', async () => {
    renderStockEventForm()

    await userEvent.click(screen.getByRole('button', { name: 'Submit' }))
    const errorBeginningDate = screen.getByTestId(
      'error-stocks[0]beginningDate'
    )
    const errorBeginningTime = screen.getByTestId(
      'error-stocks[0]beginningTime'
    )
    const errorPrice = screen.getByTestId('error-stocks[0]price')
    expect(errorBeginningDate).toBeInTheDocument()
    expect(errorBeginningTime).toBeInTheDocument()
    expect(errorPrice).toBeInTheDocument()
    expect(
      screen.queryByTestId('error-stocks[0]bookingLimitDatetime')
    ).toBeInTheDocument()
    expect(
      screen.queryByTestId('error-stocks[0]quantity')
    ).not.toBeInTheDocument()

    expect(errorBeginningDate).toHaveTextContent('Veuillez renseigner une date')
    expect(errorBeginningTime).toHaveTextContent(
      'Veuillez renseigner un horaire'
    )
    expect(errorPrice).toHaveTextContent('Veuillez renseigner un prix')
  })

  const dataSetbeginningDate: Array<number> = [
    tomorrow.getDate(),
    oneWeekLater.getDate(),
    yesterday.getDate(),
  ]
  it.each(dataSetbeginningDate)(
    'should not display beginningDate error (%s)',
    async beginningDate => {
      renderStockEventForm()
      await userEvent.click(screen.getByLabelText('Date', { exact: true }))
      await userEvent.click(screen.getByText(beginningDate))
      await userEvent.click(screen.getByLabelText('Quantité'))
      const errorbeginningDate = screen.queryByTestId(
        'error-stocks[0]beginningDate'
      )
      expect(errorbeginningDate).not.toBeInTheDocument()
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
      renderStockEventForm()

      const inputPrice = screen.getByLabelText('Prix')
      await userEvent.type(inputPrice, price)
      await userEvent.tab()
      const errorPrice = screen.queryByTestId('error-stocks[0]price')
      expect(errorPrice).toBeInTheDocument()
      expect(errorPrice).toHaveTextContent(error)
    }
  )

  const dataSetPrice = ['0', '100', '299']
  it.each(dataSetPrice)('should not display price error', async price => {
    renderStockEventForm()

    const inputPrice = screen.getByLabelText('Prix')
    await userEvent.type(inputPrice, price)
    await userEvent.tab()
    expect(screen.queryByTestId('error-stocks[0]price')).not.toBeInTheDocument()
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
      renderStockEventForm()

      const inputQuantity = screen.getByLabelText('Quantité')
      await userEvent.type(inputQuantity, quantity)
      await userEvent.tab()
      const errorquantity = screen.queryByTestId('error-stocks[0]quantity')
      expect(errorquantity).toBeInTheDocument()
      expect(errorquantity).toHaveTextContent(error)
    }
  )

  it('should display quantity error when min quantity is given', async () => {
    renderStockEventForm({ minQuantity: 10 })

    const inputQuantity = screen.getByLabelText('Quantité')
    await userEvent.type(inputQuantity, '9')
    await userEvent.tab()
    const errorquantity = screen.queryByTestId('error-stocks[0]quantity')
    expect(errorquantity).toBeInTheDocument()
    expect(errorquantity).toHaveTextContent('Quantité trop faible')
  })

  const dataSetquantity = ['0', '100', '350']
  it.each(dataSetquantity)(
    'should not display quantity error',
    async quantity => {
      renderStockEventForm()
      const inputQuantity = screen.getByLabelText('Quantité')
      await userEvent.type(inputQuantity, quantity)
      await userEvent.tab()
      expect(
        screen.queryByTestId('error-stocks[0]quantity')
      ).not.toBeInTheDocument()
    }
  )

  const dataSetBookingLimitDatetimeError = [
    {
      beginningDate: tomorrow,
      bookingLimitDatetime: tomorrow,
    },
    {
      beginningDate: oneWeekLater,
      bookingLimitDatetime: oneWeekLater,
    },
  ]
  it.each(dataSetBookingLimitDatetimeError)(
    'should not display bookingLimitDatetime error',
    async ({ beginningDate, bookingLimitDatetime }) => {
      renderStockEventForm()

      await userEvent.click(screen.getByLabelText('Date', { exact: true }))
      await userEvent.click(await screen.getByText(beginningDate.getDate()))
      expect(
        screen.queryByTestId('error-stocks[0]beginningDate')
      ).not.toBeInTheDocument()
      expect(screen.getByLabelText('Date limite de réservation')).toHaveValue(
        // DatePicker force local to fr
        formatDate(bookingLimitDatetime, 'dd/MM/yyyy')
      )

      const errorBookingLimitDatetime = screen.queryByTestId(
        'error-stocks[0]bookingLimitDatetime'
      )
      expect(errorBookingLimitDatetime).not.toBeInTheDocument()
    }
  )
})
