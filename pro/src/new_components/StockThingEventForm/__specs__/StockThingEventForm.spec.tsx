import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import { Form, Formik } from 'formik'
import React from 'react'

import { IStockThingFormProps } from 'new_components/StockThingForm/StockThingForm'
import {
  EVENT_DATE_LABEL,
  EVENT_TIME_LABEL,
} from 'screens/OfferEducationalStock/constants/labels'

import { STOCK_THING_EVENT_FORM_DEFAULT_VALUES } from '../constants'
import StockThingEventForm from '../StockThingEventForm'

const renderStockThingEventForm = (props: IStockThingFormProps) => {
  return render(
    <Formik
      initialValues={STOCK_THING_EVENT_FORM_DEFAULT_VALUES}
      onSubmit={() => {}}
    >
      <Form>
        <StockThingEventForm {...props} />
      </Form>
    </Formik>
  )
}

//TODO: coverage
describe('StockThingEventForm', () => {
  let props: IStockThingFormProps

  beforeEach(() => {
    props = {
      today: new Date(),
    }
  })

  it('render StockThingEventForm', () => {
    renderStockThingEventForm(props)

    expect(
      screen.getByLabelText(EVENT_DATE_LABEL, { exact: true })
    ).toBeInTheDocument()
    expect(screen.getByLabelText(EVENT_TIME_LABEL)).toBeInTheDocument()
    expect(screen.getByLabelText('Prix')).toBeInTheDocument()
    expect(
      screen.getByLabelText('Date limite de réservation')
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Quantité')).toBeInTheDocument()
  })

  it('render disabled field in list', () => {
    renderStockThingEventForm(props)

    expect(
      screen.getByLabelText(EVENT_DATE_LABEL, { exact: true })
    ).toBeDisabled()
    expect(screen.getByLabelText(EVENT_TIME_LABEL)).toBeDisabled()
    expect(screen.getByLabelText('Prix')).toBeDisabled()
    expect(
      screen.getByLabelText('Date limite de réservation')
    ).not.toBeDisabled()
    expect(screen.getByLabelText('Quantité')).toBeDisabled()
  })
})
