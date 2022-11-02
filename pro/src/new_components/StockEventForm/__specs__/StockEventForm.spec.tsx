import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import { Form, Formik } from 'formik'
import React from 'react'

import { STOCK_EVENT_FORM_DEFAULT_VALUES } from '../constants'
import StockEventForm, { IStockEventFormProps } from '../StockEventForm'

const renderStockEventForm = (props: IStockEventFormProps) => {
  return render(
    <Formik initialValues={STOCK_EVENT_FORM_DEFAULT_VALUES} onSubmit={() => {}}>
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
    }
  })

  it('render StockEventForm', () => {
    renderStockEventForm(props)

    expect(screen.getByLabelText('Date', { exact: true })).toBeInTheDocument()
    expect(screen.getByLabelText('Horraire')).toBeInTheDocument()
    expect(screen.getByLabelText('Prix')).toBeInTheDocument()
    expect(
      screen.getByLabelText('Date limite de réservation')
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Quantité')).toBeInTheDocument()

    expect(screen.getByLabelText('Date', { exact: true })).not.toBeDisabled()
    expect(screen.getByLabelText('Horraire')).not.toBeDisabled()
    expect(screen.getByLabelText('Prix')).not.toBeDisabled()
    expect(
      screen.getByLabelText('Date limite de réservation')
    ).not.toBeDisabled()
    expect(screen.getByLabelText('Quantité')).not.toBeDisabled()
  })

  it('render disabled field in list', () => {
    props.readOnlyFields = [
      'eventDatetime',
      'eventTime',
      'bookingLimitDatetime',
      'price',
      'quantity',
    ]
    renderStockEventForm(props)

    expect(screen.getByLabelText('Date', { exact: true })).toBeDisabled()
    expect(screen.getByLabelText('Horraire')).toBeDisabled()
    expect(screen.getByLabelText('Prix')).toBeDisabled()
    expect(screen.getByLabelText('Date limite de réservation')).toBeDisabled()
    expect(screen.getByLabelText('Quantité')).toBeDisabled()
  })
})
