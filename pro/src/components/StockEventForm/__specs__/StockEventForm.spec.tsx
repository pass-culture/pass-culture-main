import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'

import { STOCK_EVENT_FORM_DEFAULT_VALUES } from '../constants'
import StockEventForm, { IStockEventFormProps } from '../StockEventForm'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2022-12-20T00:00:00Z')),
}))

const renderStockEventForm = (
  props: IStockEventFormProps,
  initialStock = STOCK_EVENT_FORM_DEFAULT_VALUES
) => {
  return render(
    <Formik initialValues={{ stocks: [initialStock] }} onSubmit={() => {}}>
      <Form>
        <StockEventForm {...props} />
      </Form>
    </Formik>
  )
}

describe('StockEventForm', () => {
  let props: IStockEventFormProps

  beforeEach(() => {
    props = {
      today: new Date(),
      stockIndex: 0,
    }
  })

  it('render StockEventForm', () => {
    renderStockEventForm(props)

    expect(screen.getByLabelText('Date', { exact: true })).toBeInTheDocument()
    expect(screen.getByLabelText('Horaire')).toBeInTheDocument()
    expect(screen.getByLabelText('Prix')).toBeInTheDocument()
    expect(
      screen.getByLabelText('Date limite de réservation')
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Quantité')).toBeInTheDocument()

    expect(screen.getByLabelText('Date', { exact: true })).not.toBeDisabled()
    expect(screen.getByLabelText('Horaire')).not.toBeDisabled()
    expect(screen.getByLabelText('Prix')).not.toBeDisabled()
    expect(
      screen.getByLabelText('Date limite de réservation')
    ).not.toBeDisabled()
    expect(screen.getByLabelText('Quantité')).not.toBeDisabled()
  })

  it('render disabled field in list', () => {
    renderStockEventForm(props, {
      ...STOCK_EVENT_FORM_DEFAULT_VALUES,
      readOnlyFields: [
        'beginningDate',
        'beginningTime',
        'bookingLimitDatetime',
        'price',
        'quantity',
      ],
    })

    expect(screen.getByLabelText('Date', { exact: true })).toBeDisabled()
    expect(screen.getByLabelText('Horaire')).toBeDisabled()
    expect(screen.getByLabelText('Prix')).toBeDisabled()
    expect(screen.getByLabelText('Date limite de réservation')).toBeDisabled()
    expect(screen.getByLabelText('Quantité')).toBeDisabled()
  })
  it('should set stockBookingLimitDatetime at event date if date changed before stockBookingLimitDatetime', async () => {
    const initialStock = {
      beginningDate: new Date('2022-12-29T00:00:00Z'),
      beginningTime: new Date('2022-12-29T00:00:00Z'),
      remainingQuantity: '11',
      bookingsQuantity: '1',
      quantity: '12',
      bookingLimitDatetime: new Date('2022-12-28T00:00:00Z'),
      price: '10',
      isDeletable: true,
      readOnlyFields: [],
    }

    renderStockEventForm(props, initialStock)

    await userEvent.click(screen.getByLabelText('Date'))
    await userEvent.click(screen.getByText(27))

    expect(screen.getByLabelText('Date limite de réservation')).toHaveValue(
      '27/12/2022'
    )
  })
})
