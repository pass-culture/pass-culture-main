import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import { Form, Formik } from 'formik'
import React from 'react'

import { STOCK_THING_FORM_DEFAULT_VALUES } from '../constants'
import StockThingForm, { IStockThingFormProps } from '../StockThingForm'

const renderStockThingForm = (props: IStockThingFormProps) => {
  return render(
    <Formik initialValues={STOCK_THING_FORM_DEFAULT_VALUES} onSubmit={() => {}}>
      <Form>
        <StockThingForm {...props} />
      </Form>
    </Formik>
  )
}

describe('StockThingForm', () => {
  let props: IStockThingFormProps

  beforeEach(() => {
    props = {
      today: new Date(),
    }
  })

  it('render StockThingForm', () => {
    renderStockThingForm(props)

    expect(screen.getByLabelText('Prix')).toBeInTheDocument()
    expect(
      screen.getByLabelText('Date limite de réservation')
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Quantité')).toBeInTheDocument()
  })

  it('render disabled field in list', () => {
    props.readOnlyFields = ['price', 'quantity']
    renderStockThingForm(props)

    expect(screen.getByLabelText('Prix')).toBeDisabled()
    expect(
      screen.getByLabelText('Date limite de réservation')
    ).not.toBeDisabled()
    expect(screen.getByLabelText('Quantité')).toBeDisabled()
  })
})
