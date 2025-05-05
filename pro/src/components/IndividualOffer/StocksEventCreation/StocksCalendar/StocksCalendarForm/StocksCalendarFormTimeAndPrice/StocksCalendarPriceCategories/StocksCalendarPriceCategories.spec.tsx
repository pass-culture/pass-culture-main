import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import { renderWithProviders } from 'commons/utils/renderWithProviders'
import {
  DurationTypeOption,
  StocksCalendarFormValues,
  TimeSlotTypeOption,
} from 'components/IndividualOffer/StocksEventCreation/form/types'

import { StocksCalendarPriceCategories } from './StocksCalendarPriceCategories'

function renderStocksCalendarPriceCategories(
  defaultOptions?: Partial<StocksCalendarFormValues>
) {
  function StocksCalendarPriceCategoriesWrapper() {
    const form = useForm<StocksCalendarFormValues>({
      defaultValues: {
        durationType: DurationTypeOption.ONE_DAY,
        timeSlotType: TimeSlotTypeOption.SPECIFIC_TIME,
        specificTimeSlots: [{ slot: '' }],
        pricingCategoriesQuantities: [{ priceCategory: '' }],
        oneDayDate: '',
        ...defaultOptions,
      },
    })

    return (
      <FormProvider {...form}>
        <StocksCalendarPriceCategories
          form={form}
          priceCategories={[
            { id: 1, label: 'Tarif 1', price: 10 },
            { id: 2, label: 'Tarif 2', price: 20 },
          ]}
        />
      </FormProvider>
    )
  }

  return renderWithProviders(<StocksCalendarPriceCategoriesWrapper />)
}

describe('StocksCalendarPriceCategories', () => {
  it('should display price and category inputs', () => {
    renderStocksCalendarPriceCategories()

    expect(screen.getByLabelText('Nombre de places')).toBeInTheDocument()
    expect(screen.getByLabelText('Illimité')).toBeChecked()
  })

  it('should uncheck the unlimited checkbox when a valid price is typed', async () => {
    renderStocksCalendarPriceCategories()

    expect(screen.getByLabelText('Illimité')).toBeChecked()

    await userEvent.type(screen.getByLabelText('Nombre de places'), '10')

    expect(screen.getByLabelText('Illimité')).not.toBeChecked()
  })

  it('should check the unlimited checkbox when the price is cleared', async () => {
    renderStocksCalendarPriceCategories({
      pricingCategoriesQuantities: [{ quantity: 10, priceCategory: '1' }],
    })

    expect(screen.getByLabelText('Illimité')).not.toBeChecked()

    await userEvent.clear(screen.getByLabelText('Nombre de places'))

    expect(screen.getByLabelText('Illimité')).toBeChecked()
  })

  it('should clear the quantity when the unlimited checkbox is checked', async () => {
    renderStocksCalendarPriceCategories({
      pricingCategoriesQuantities: [{ quantity: 10, priceCategory: '1' }],
    })

    expect(screen.getByLabelText('Nombre de places')).toHaveValue(10)

    await userEvent.click(screen.getByLabelText('Illimité'))

    expect(screen.getByLabelText('Nombre de places')).toHaveValue(null)
  })

  it('should be able to remove a price and category when there are more than two', async () => {
    renderStocksCalendarPriceCategories({
      pricingCategoriesQuantities: [{ quantity: 10, priceCategory: '1' }],
    })

    expect(
      screen.queryByRole('button', { name: 'Supprimer les places' })
    ).not.toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Ajouter d’autres places et tarifs' })
    )

    expect(
      screen.getAllByRole('button', { name: 'Supprimer les places' })
    ).toHaveLength(2)

    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer les places' })[0]
    )

    expect(
      screen.queryByRole('button', { name: 'Supprimer les places' })
    ).not.toBeInTheDocument()
  })
})
