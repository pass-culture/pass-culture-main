import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import { SubmitButton } from 'ui-kit'

import { STOCK_THING_FORM_DEFAULT_VALUES } from '../constants'
import StockThingForm, { IStockThingFormProps } from '../StockThingForm'
import { getValidationSchema } from '../validationSchema'

const renderStockThingForm = ({
  minQuantity = null,
}: {
  minQuantity?: number | null
} = {}) => {
  const props: IStockThingFormProps = { today: new Date() }
  return render(
    <Formik
      initialValues={STOCK_THING_FORM_DEFAULT_VALUES}
      onSubmit={() => {}}
      validationSchema={getValidationSchema(minQuantity)}
    >
      {({ handleSubmit }) => (
        <form onSubmit={handleSubmit}>
          <StockThingForm {...props} />
          <SubmitButton>Submit</SubmitButton>
        </form>
      )}
    </Formik>
  )
}

describe('StockThingForm:validationSchema', () => {
  it('test required fields', async () => {
    renderStockThingForm()
    await userEvent.click(screen.getByRole('button', { name: 'Submit' }))
    expect(screen.getByTestId('error-price')).toBeInTheDocument()
    expect(
      screen.queryByTestId('error-bookingLimitDatetime')
    ).not.toBeInTheDocument()
    expect(screen.queryByTestId('error-quantity')).not.toBeInTheDocument()
  })

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
      renderStockThingForm()
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
    renderStockThingForm()
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
      renderStockThingForm()
      const inputQuantity = screen.getByLabelText('Quantité')
      await userEvent.type(inputQuantity, quantity)
      await userEvent.tab()
      const errorquantity = screen.queryByTestId('error-quantity')
      expect(errorquantity).toBeInTheDocument()
      expect(errorquantity).toHaveTextContent(error)
    }
  )
  it('should display quantity error when min quantity is given', async () => {
    renderStockThingForm({ minQuantity: 10 })
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
      renderStockThingForm()
      const inputQuantity = screen.getByLabelText('Quantité')
      await userEvent.type(inputQuantity, quantity)
      await userEvent.tab()
      expect(screen.queryByTestId('error-quantity')).not.toBeInTheDocument()
    }
  )
})
