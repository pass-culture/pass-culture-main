import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import { SubmitButton } from 'ui-kit'
import { getToday } from 'utils/date'
import { renderWithProviders } from 'utils/renderWithProviders'

import { STOCK_EVENT_FORM_DEFAULT_VALUES } from '../constants'
import StockEventForm, { IStockEventFormProps } from '../StockEventForm'
import { IStockEventFormValues } from '../types'
import { getValidationSchema } from '../validationSchema'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2022-12-15T00:00:00Z')),
}))

const today = getToday()
const tomorrow = getToday()
const yesterday = getToday()
const oneWeekLater = getToday()
tomorrow.setDate(tomorrow.getDate() + 1)
yesterday.setDate(yesterday.getDate() - 1)
oneWeekLater.setDate(oneWeekLater.getDate() + 7)

const renderStockEventForm = (
  initialValues: IStockEventFormValues = STOCK_EVENT_FORM_DEFAULT_VALUES,
  // TODO remove when WIP_ENABLE_MULTI_PRICE_STOCKS is removed
  isPriceCategoriesActive = false
) => {
  const props: IStockEventFormProps = {
    today,
    stockIndex: 0,
    priceCategoriesOptions: [
      { label: 'Tarif 1', value: '1' },
      { label: 'Tarif 2', value: '2' },
    ],
  }

  return renderWithProviders(
    <Formik
      initialValues={{
        stocks: [initialValues],
      }}
      onSubmit={jest.fn()}
      validationSchema={getValidationSchema(
        props.priceCategoriesOptions,
        isPriceCategoriesActive
      )}
    >
      {({ handleSubmit }) => (
        <form onSubmit={handleSubmit}>
          <StockEventForm {...props} />
          <SubmitButton>Submit</SubmitButton>
        </form>
      )}
    </Formik>,
    {
      storeOverrides: {
        features: {
          list: [
            {
              isActive: isPriceCategoriesActive,
              nameKey: 'WIP_ENABLE_MULTI_PRICE_STOCKS',
            },
          ],
        },
      },
    }
  )
}

describe('StockEventForm:validationSchema', () => {
  // TODO remove when WIP_ENABLE_MULTI_PRICE_STOCKS is removed
  it('test required fields (old)', async () => {
    renderStockEventForm()

    await userEvent.click(screen.getByRole('button', { name: 'Submit' }))
    const errorBeginningDate = screen.getByTestId(
      'error-stocks[0]beginningDate'
    )
    const errorBeginningTime = screen.getByTestId(
      'error-stocks[0]beginningTime'
    )
    const errorPrice = screen.getByTestId('error-stocks[0]price')
    expect(errorBeginningDate).toBeInTheDocument()
    expect(errorBeginningTime).toBeInTheDocument()
    expect(errorPrice).toBeInTheDocument()
    expect(
      screen.queryByTestId('error-stocks[0]quantity')
    ).not.toBeInTheDocument()

    expect(errorBeginningDate).toHaveTextContent('Veuillez renseigner une date')
    expect(errorBeginningTime).toHaveTextContent(
      'Veuillez renseigner un horaire'
    )
    expect(errorPrice).toHaveTextContent('Veuillez renseigner un prix')
  })

  it.only('shoudld validate required fields', async () => {
    renderStockEventForm(undefined, true)

    await userEvent.click(screen.getByRole('button', { name: 'Submit' }))
    const errorBeginningDate = screen.getByTestId(
      'error-stocks[0]beginningDate'
    )
    const errorBeginningTime = screen.getByTestId(
      'error-stocks[0]beginningTime'
    )
    const errorPriceCategory = screen.getByTestId(
      'error-stocks[0]priceCategoryId'
    )
    expect(errorBeginningDate).toBeInTheDocument()
    expect(errorBeginningTime).toBeInTheDocument()
    expect(errorPriceCategory).toBeInTheDocument()
    expect(
      screen.queryByTestId('error-stocks[0]quantity')
    ).not.toBeInTheDocument()

    expect(errorBeginningDate).toHaveTextContent('Veuillez renseigner une date')
    expect(errorBeginningTime).toHaveTextContent(
      'Veuillez renseigner un horaire'
    )
    expect(errorPriceCategory).toHaveTextContent('Veuillez renseigner un tarif')
  })

  const dataSetbeginningDate: Array<number> = [
    tomorrow.getDate(),
    oneWeekLater.getDate(),
    yesterday.getDate(),
  ]
  it.each(dataSetbeginningDate)(
    'should not display beginningDate error (%s)',
    async beginningDate => {
      renderStockEventForm()
      await userEvent.click(screen.getByLabelText('Date', { exact: true }))
      await userEvent.click(screen.getByText(beginningDate))
      await userEvent.click(screen.getByLabelText('Quantité'))
      const errorbeginningDate = screen.queryByTestId(
        'error-stocks[0]beginningDate'
      )
      expect(errorbeginningDate).not.toBeInTheDocument()
    }
  )

  it('should display price error %s', async () => {
    renderStockEventForm()

    const inputPrice = screen.getByLabelText('Tarif')
    await userEvent.type(inputPrice, '301')
    await userEvent.tab()
    const errorPrice = screen.queryByTestId('error-stocks[0]price')
    expect(errorPrice).toBeInTheDocument()
    expect(errorPrice).toHaveTextContent(
      'Veuillez renseigner un prix inférieur à 300€'
    )
  })

  const dataSetPrice = ['0', '100', '299']
  it.each(dataSetPrice)('should not display price error', async price => {
    renderStockEventForm()
    const inputPrice = screen.getByLabelText('Tarif')
    await userEvent.type(inputPrice, price)
    await userEvent.tab()
    expect(screen.queryByTestId('error-stocks[0]price')).not.toBeInTheDocument()
  })

  it('should display quantity error when min quantity is given', async () => {
    renderStockEventForm({
      ...STOCK_EVENT_FORM_DEFAULT_VALUES,
      bookingsQuantity: '10',
    })

    const inputQuantity = screen.getByLabelText('Quantité')
    await userEvent.type(inputQuantity, '9')
    await userEvent.tab()
    const errorquantity = screen.queryByTestId('error-stocks[0]quantity')
    expect(errorquantity).toBeInTheDocument()
    expect(errorquantity).toHaveTextContent('Quantité trop faible')
  })

  const dataSetquantity = ['0', '100', '350']
  it.each(dataSetquantity)(
    'should not display quantity error',
    async quantity => {
      renderStockEventForm()
      const inputQuantity = screen.getByLabelText('Quantité')
      await userEvent.type(inputQuantity, quantity)
      await userEvent.tab()
      expect(
        screen.queryByTestId('error-stocks[0]quantity')
      ).not.toBeInTheDocument()
    }
  )
})
