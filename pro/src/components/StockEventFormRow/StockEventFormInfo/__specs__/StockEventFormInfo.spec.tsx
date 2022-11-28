import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import { Form, Formik } from 'formik'
import React from 'react'

import StockFormInfo from '../StockEventFormInfo'

const renderStockFormInfo = () => {
  const stock = {
    stockId: 'STOCK_ID',
    beginningDate: new Date('2022-10-26T00:00:00.0200'),
    beginningTime: new Date('2022-10-26T00:00:00.0200'),
    remainingQuantity: '17',
    bookingsQuantity: '20',
    quantity: '40',
    bookingLimitDatetime: new Date('2022-10-26T00:00:00.0200'),
    price: '12.13',
    isDeletable: true,
  }
  return render(
    <Formik initialValues={{ stocks: [stock] }} onSubmit={() => {}}>
      <Form>
        <StockFormInfo index={0} />
      </Form>
    </Formik>
  )
}

describe('StockFormInfo', () => {
  it('render', async () => {
    renderStockFormInfo()
    expect(screen.getByText('Stock restant')).toBeInTheDocument()
    expect(screen.getByText('Réservations')).toBeInTheDocument()
    expect(screen.getByText('Stock restant')).toBeInTheDocument()
    expect(screen.getByText('17')).toBeInTheDocument()
  })
})
