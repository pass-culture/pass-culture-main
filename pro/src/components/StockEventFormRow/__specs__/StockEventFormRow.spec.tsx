import { fireEvent, render, screen } from '@testing-library/react'
import { Form, Formik } from 'formik'
import React from 'react'

import {
  IStockEventFormValues,
  StockEventForm,
  STOCK_EVENT_FORM_DEFAULT_VALUES,
} from 'components/StockEventForm'

import StockFormRow, { IStockEventFormRowProps } from '../StockEventFormRow'

interface IRenderStockFormRowArgs {
  props: IStockEventFormRowProps
  initialValues: IStockEventFormValues
}
const renderStockFormRow = ({
  props,
  initialValues,
}: IRenderStockFormRowArgs) => {
  return render(
    <Formik initialValues={{ stocks: [initialValues] }} onSubmit={() => {}}>
      <Form>
        <StockFormRow {...props}>
          <StockEventForm today={new Date()} stockIndex={0} />
        </StockFormRow>
      </Form>
    </Formik>
  )
}

describe('StockFormRow', () => {
  let props: IStockEventFormRowProps
  let initialValues: IStockEventFormValues

  beforeEach(() => {
    props = {
      showStockInfo: true,
      stockIndex: 0,
      actions: [
        {
          callback: () => {},
          label: 'Action label',
        },
      ],
      actionDisabled: false,
    }
    initialValues = {
      ...STOCK_EVENT_FORM_DEFAULT_VALUES,
      price: 12,
      stockId: 'STOCK_ID',
      quantity: 10,
      bookingsQuantity: '4',
      remainingQuantity: '6',
    }
  })

  it('render StockEventFormRow', () => {
    renderStockFormRow({
      props: {
        ...props,
        showStockInfo: true,
      },
      initialValues,
    })

    expect(screen.getByLabelText('Date')).toBeInTheDocument()
    expect(screen.getByLabelText('Horaire')).toBeInTheDocument()
    expect(screen.getByLabelText('Tarif')).toBeInTheDocument()
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

  it('should set remainQuantity to unlimited on quantity change', async () => {
    await await renderStockFormRow({
      props: {
        ...props,
        showStockInfo: true,
      },
      initialValues,
    })
    const quantityInput = await screen.getByLabelText('Quantité', {
      exact: false,
    })
    expect(screen.getByLabelText('Quantité')).toHaveValue(10)
    expect(screen.queryAllByText('Illimité').length).toBe(0)

    fireEvent.change(quantityInput, { target: { value: '' } })
    expect(screen.queryAllByText('Illimité').length).toBe(1)
  })
})
