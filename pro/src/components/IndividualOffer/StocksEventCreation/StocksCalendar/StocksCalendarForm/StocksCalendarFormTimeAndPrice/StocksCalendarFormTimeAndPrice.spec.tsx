import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import { getIndividualOfferFactory } from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import {
  DurationTypeOption,
  StocksCalendarFormValues,
  TimeSlotTypeOption,
} from 'components/IndividualOffer/StocksEventCreation/form/types'

import { StocksCalendarFormTimeAndPrice } from './StocksCalendarFormTimeAndPrice'

function renderStocksCalendarFormTimeAndPrice(
  defaultOptions?: Partial<StocksCalendarFormValues>
) {
  function StocksCalendarFormTimeAndPriceWrapper() {
    const form = useForm<StocksCalendarFormValues>({
      defaultValues: {
        durationType: DurationTypeOption.ONE_DAY,
        timeSlotType: TimeSlotTypeOption.SPECIFIC_TIME,
        specificTimeSlots: [{ slot: '' }],
        pricingCategoriesQuantities: [{ isUnlimited: true, priceCategory: '' }],
        oneDayDate: '',
        ...defaultOptions,
      },
    })

    return (
      <FormProvider {...form}>
        <StocksCalendarFormTimeAndPrice
          form={form}
          offer={getIndividualOfferFactory()}
        />
      </FormProvider>
    )
  }

  return renderWithProviders(<StocksCalendarFormTimeAndPriceWrapper />)
}

describe('StocksCalendarFormTimeAndPrice', () => {
  it('should show a time slot type radio group choice', () => {
    renderStocksCalendarFormTimeAndPrice()
    expect(
      screen.getByLabelText('Le public doit se présenter :')
    ).toBeInTheDocument()
  })

  it('should show an error callout when trying to set specific time slots for multplie days without an end date', async () => {
    renderStocksCalendarFormTimeAndPrice({
      durationType: DurationTypeOption.MULTIPLE_DAYS_WEEKS,
      timeSlotType: TimeSlotTypeOption.OPENING_HOURS,
      multipleDaysHasNoEndDate: true,
    })
    expect(
      screen.queryByText(
        'En n’indiquant pas de date de fin, vous ne pouvez pas choisir l’option horaires précis.'
      )
    ).not.toBeInTheDocument()

    await userEvent.click(screen.getByLabelText(/À un horaire précis/))

    expect(
      screen.getByText(
        'En n’indiquant pas de date de fin, vous ne pouvez pas choisir l’option horaires précis.'
      )
    ).toBeInTheDocument()
  })
})
