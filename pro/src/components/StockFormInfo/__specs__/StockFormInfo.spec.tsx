import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import { Form, Formik } from 'formik'
import React from 'react'

import { STOCK_THING_FORM_DEFAULT_VALUES } from 'components/StockThingForm'

import StockFormInfo from '../StockFormInfo'

const renderStockFormInfo = () => {
  return render(
    <Formik initialValues={STOCK_THING_FORM_DEFAULT_VALUES} onSubmit={() => {}}>
      <Form>
        <StockFormInfo />
      </Form>
    </Formik>
  )
}

describe('StockFormInfo', () => {
  it('render', async () => {
    renderStockFormInfo()
    expect(screen.getByText('Stock restant')).toBeInTheDocument()
    expect(screen.getByText('Réservations')).toBeInTheDocument()
    expect(screen.getByText('Illimité')).toBeInTheDocument()
  })
})
