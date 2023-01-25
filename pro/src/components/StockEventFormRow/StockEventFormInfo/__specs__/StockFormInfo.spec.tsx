import { render, screen } from '@testing-library/react'
import { Form, Formik } from 'formik'
import React from 'react'

import { STOCK_THING_FORM_DEFAULT_VALUES } from 'components/StockThingForm'

import StockEventFormInfo from '../StockEventFormInfo'

const renderStockFormInfo = () => {
  return render(
    <Formik
      initialValues={{ stocks: [STOCK_THING_FORM_DEFAULT_VALUES] }}
      onSubmit={() => {}}
    >
      <Form>
        <StockEventFormInfo stockIndex={0} />
      </Form>
    </Formik>
  )
}

describe('StockFormInfo', () => {
  it('render', () => {
    renderStockFormInfo()
    expect(screen.getByText('Stock restant')).toBeInTheDocument()
    expect(screen.getByText('Réservations')).toBeInTheDocument()
    expect(screen.getByText('Illimité')).toBeInTheDocument()
  })
})
