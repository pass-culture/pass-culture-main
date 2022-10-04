import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import { Form, Formik } from 'formik'
import React from 'react'

import {
  IStockThingFormValues,
  StockThingForm,
  STOCK_THING_FORM_DEFAULT_VALUES,
} from 'new_components/StockThingForm'

import StockFormRow, { IStockFormRowProps } from '../StockFormRow'

interface IRenderStockFormRowArgs {
  props: IStockFormRowProps
  initialValues: IStockThingFormValues
}
const renderStockFormRow = ({
  props,
  initialValues,
}: IRenderStockFormRowArgs) => {
  return render(
    <Formik initialValues={initialValues} onSubmit={() => {}}>
      <Form>
        <StockFormRow {...props} />
      </Form>
    </Formik>
  )
}

describe('StockFormRow', () => {
  let props: IStockFormRowProps
  let initialValues: IStockThingFormValues

  beforeEach(() => {
    props = {
      Form: <StockThingForm today={new Date()} />,
      actions: [
        {
          callback: () => {},
          label: 'Action label',
        },
      ],
      actionDisabled: false,
    }
    initialValues = {
      ...STOCK_THING_FORM_DEFAULT_VALUES,
      stockId: 'STOCK_ID',
      quantity: '10',
      bookingsQuantity: '4',
      remainingQuantity: '6',
    }
  })

  it('render StockFormRow', () => {
    renderStockFormRow({ props, initialValues })

    expect(screen.getByLabelText('Prix')).toBeInTheDocument()
    expect(
      screen.getByLabelText('Date limite de réservation')
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Quantité')).toBeInTheDocument()

    expect(screen.getByText('Stock restant')).toBeInTheDocument()
    expect(screen.getByText('Réservations')).toBeInTheDocument()

    expect(
      screen.getByTestId('stock-form-actions-button-open')
    ).toBeInTheDocument()
  })

  it('should not render actions', () => {
    props.actions = []
    renderStockFormRow({ props, initialValues })

    expect(screen.getByLabelText('Prix')).toBeInTheDocument()
    expect(
      screen.getByLabelText('Date limite de réservation')
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Quantité')).toBeInTheDocument()

    expect(screen.getByText('Stock restant')).toBeInTheDocument()
    expect(screen.getByText('Réservations')).toBeInTheDocument()

    expect(
      screen.queryByTestId('stock-form-actions-button-open')
    ).not.toBeInTheDocument()
  })

  it('should not render stock informations', () => {
    initialValues = STOCK_THING_FORM_DEFAULT_VALUES
    renderStockFormRow({ props, initialValues })

    expect(screen.getByLabelText('Prix')).toBeInTheDocument()
    expect(
      screen.getByLabelText('Date limite de réservation')
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Quantité')).toBeInTheDocument()

    expect(screen.queryByText('Stock restant')).not.toBeInTheDocument()
    expect(screen.queryByText('Réservations')).not.toBeInTheDocument()

    expect(
      screen.getByTestId('stock-form-actions-button-open')
    ).toBeInTheDocument()
  })
})
