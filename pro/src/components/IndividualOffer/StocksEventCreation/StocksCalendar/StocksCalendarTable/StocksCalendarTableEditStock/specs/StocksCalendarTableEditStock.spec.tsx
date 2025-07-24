import * as Dialog from '@radix-ui/react-dialog'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'
import { FormProvider, useForm } from 'react-hook-form'

import { getOfferStockFactory } from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import {
  EditStockFormValues,
  StocksCalendarTableEditStock,
  StocksCalendarTableEditStockProps,
} from '../StocksCalendarTableEditStock'

function renderStocksCalendarTableEditStock(
  props?: Partial<StocksCalendarTableEditStockProps>
) {
  function StocksCalendarTableEditStockWrapper() {
    const form = useForm<EditStockFormValues>({
      defaultValues: {
        date: '2021-10-15T12:00:00Z',
        time: '12:00',
        priceCategory: '1',
        bookingLimitDate: '2021-09-15T21:59:59Z',
        quantity: 1,
        ...props,
      },
    })
    return (
      <Dialog.Root>
        <FormProvider {...form}>
          <StocksCalendarTableEditStock
            departmentCode="56"
            stock={getOfferStockFactory()}
            priceCategories={[{ id: 1, label: 'tarif', price: 12 }]}
            onUpdateStock={() => vi.fn()}
            {...props}
          />
        </FormProvider>
      </Dialog.Root>
    )
  }
  renderWithProviders(<StocksCalendarTableEditStockWrapper />)
}

describe('StocksCalendarTableEditStock', () => {
  it('should set the stock initial form values on init', () => {
    const beginningDate = addDays(new Date(), 2).toISOString().split('T')[0]
    const limitDate = addDays(new Date(), 3).toISOString().split('T')[0]
    const priceCategoryId = 1
    const quantity = 322

    renderStocksCalendarTableEditStock({
      stock: getOfferStockFactory({
        beginningDatetime: beginningDate,
        bookingLimitDatetime: limitDate,
        priceCategoryId: priceCategoryId,
        quantity: quantity,
      }),
    })

    expect(screen.getAllByLabelText('Date *')[0]).toHaveValue(beginningDate)
    expect(screen.getByLabelText('Tarif *')).toHaveValue(
      priceCategoryId.toString()
    )
    expect(screen.getByLabelText('Nombre de places')).toHaveValue(quantity)
    expect(screen.getAllByLabelText('Date *')[1]).toHaveValue(limitDate)
  })

  it('should check the unlimited checkbox initially if the quantity does not exist', () => {
    renderStocksCalendarTableEditStock({
      stock: getOfferStockFactory({
        quantity: null,
      }),
    })

    expect(screen.getByLabelText('Illimité')).toBeChecked()
  })

  it('should clear the quantity input when the unlimited checkbox is checked', async () => {
    renderStocksCalendarTableEditStock({
      stock: getOfferStockFactory({
        quantity: 12,
      }),
    })

    await userEvent.click(screen.getByLabelText('Illimité'))

    expect(screen.getByLabelText('Nombre de places')).toHaveValue(null)
  })

  it('should uncheck the unlimited checkbox when the quantity input is filled', async () => {
    renderStocksCalendarTableEditStock({
      stock: getOfferStockFactory({
        quantity: null,
      }),
    })

    await userEvent.type(screen.getByLabelText('Nombre de places'), '12')

    expect(screen.getByLabelText('Illimité')).not.toBeChecked()
  })

  it('should let edit quantity with 0', async () => {
    renderStocksCalendarTableEditStock({
      stock: getOfferStockFactory({
        quantity: 12,
      }),
    })

    await userEvent.clear(screen.getByLabelText('Nombre de places'))
    await userEvent.type(screen.getByLabelText('Nombre de places'), '0')
    await userEvent.click(screen.getByRole('button', { name: 'Valider' }))

    expect(
      screen.queryByText('Veuillez indiquer une quantité supérieure à 0')
    ).not.toBeInTheDocument()
  })
})
