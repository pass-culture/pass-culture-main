import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import { IStockThingFormProps } from 'new_components/StockThingForm/StockThingForm'
import { SubmitButton } from 'ui-kit'
import { getToday } from 'utils/date'

import { STOCK_EVENT_FORM_DEFAULT_VALUES } from '../constants'
import StockEventForm from '../StockEventForm'
import { getValidationSchema } from '../validationSchema'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2022-12-15T00:00:00Z')),
}))

const today = getToday()
const tomorrow = getToday()
const oneWeekLater = getToday()
tomorrow.setDate(tomorrow.getDate() + 1)
oneWeekLater.setDate(oneWeekLater.getDate() + 7)

const renderStockEventForm = ({
  minQuantity,
  onSubmit = jest.fn(),
}: {
  minQuantity?: number | null
  onSubmit?: () => void
} = {}) => {
  const props: IStockThingFormProps = { today }
  return render(
    <Formik
      initialValues={STOCK_EVENT_FORM_DEFAULT_VALUES}
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
    expect(screen.getByTestId('error-beginningDate')).toBeInTheDocument()
    expect(screen.getByTestId('error-beginningTime')).toBeInTheDocument()
    expect(screen.getByTestId('error-price')).toBeInTheDocument()
    expect(
      screen.queryByTestId('error-bookingLimitDatetime')
    ).not.toBeInTheDocument()
    expect(screen.queryByTestId('error-quantity')).not.toBeInTheDocument()
  })

  const dataSetbeginningDateError = [
    {
      beginningDate: today.getDate(),
      error: "La date de l'évènement doit être supérieure à aujourd'hui",
    },
  ]
  it.each(dataSetbeginningDateError)(
    'should display beginningDate error',
    async ({ beginningDate, error }) => {
      renderStockEventForm()

      await userEvent.click(screen.getByLabelText('Date', { exact: true }))
      await userEvent.click(screen.getByText(beginningDate))
      const errorbeginningDate = screen.queryByTestId('error-beginningDate')
      expect(errorbeginningDate).toBeInTheDocument()
      expect(errorbeginningDate).toHaveTextContent(error)
    }
  )

  const dataSetbeginningDate: Array<number> = [
    tomorrow.getDate(),
    oneWeekLater.getDate(),
  ]
  it.each(dataSetbeginningDate)(
    'should not display beginningDate error',
    async beginningDate => {
      renderStockEventForm()

      await userEvent.click(screen.getByLabelText('Date', { exact: true }))
      await userEvent.click(screen.getByText(beginningDate))
      const errorbeginningDate = screen.queryByTestId('error-beginningDate')
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
      const errorPrice = screen.queryByTestId('error-price')
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
      renderStockEventForm()

      const inputQuantity = screen.getByLabelText('Quantité')
      await userEvent.type(inputQuantity, quantity)
      await userEvent.tab()
      const errorquantity = screen.queryByTestId('error-quantity')
      expect(errorquantity).toBeInTheDocument()
      expect(errorquantity).toHaveTextContent(error)
    }
  )

  it('should display quantity error when min quantity is given', async () => {
    renderStockEventForm({ minQuantity: 10 })

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
      renderStockEventForm()
      const inputQuantity = screen.getByLabelText('Quantité')
      await userEvent.type(inputQuantity, quantity)
      await userEvent.tab()
      expect(screen.queryByTestId('error-quantity')).not.toBeInTheDocument()
    }
  )

  it('should display bookingLimitDatetime error when bookingLimitDatetime > beginningDate', async () => {
    renderStockEventForm()

    await userEvent.click(screen.getByLabelText('Date', { exact: true }))
    await userEvent.click(screen.getByText(tomorrow.getDate()))

    const errorbeginningDate = screen.queryByTestId('error-beginningDate')
    expect(errorbeginningDate).not.toBeInTheDocument()

    await userEvent.click(screen.getByLabelText('Date limite de réservation'))
    await userEvent.click(screen.getByText(oneWeekLater.getDate()))

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
      beginningDate: oneWeekLater.getDate(),
      bookingLimitDatetime: tomorrow.getDate(),
    },
    {
      beginningDate: oneWeekLater.getDate(),
      bookingLimitDatetime: oneWeekLater.getDate(),
    },
  ]
  it.each(dataSetBookingLimitDatetimeError)(
    'should not display bookingLimitDatetime error',
    async ({ beginningDate, bookingLimitDatetime }) => {
      renderStockEventForm()

      await userEvent.click(screen.getByLabelText('Date', { exact: true }))
      await userEvent.click(screen.getByText(beginningDate))
      const errorbeginningDate = screen.queryByTestId('error-beginningDate')
      expect(errorbeginningDate).not.toBeInTheDocument()

      await userEvent.click(screen.getByLabelText('Date limite de réservation'))
      await userEvent.click(screen.getByText(bookingLimitDatetime))

      const errorBookingLimitDatetime = screen.queryByTestId(
        'error-bookingLimitDatetime'
      )
      expect(errorBookingLimitDatetime).not.toBeInTheDocument()
    }
  )
})
