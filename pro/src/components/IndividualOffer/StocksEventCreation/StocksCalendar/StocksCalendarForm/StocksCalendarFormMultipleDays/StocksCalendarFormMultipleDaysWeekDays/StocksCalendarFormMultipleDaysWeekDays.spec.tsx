import { screen } from '@testing-library/react'
import { addDays, getISODay } from 'date-fns'
import { FormProvider, useForm } from 'react-hook-form'

import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { weekDays } from 'components/IndividualOffer/StocksEventCreation/form/constants'
import {
  DurationTypeOption,
  StocksCalendarFormValues,
  TimeSlotTypeOption,
} from 'components/IndividualOffer/StocksEventCreation/form/types'

import { StocksCalendarFormMultipleDaysWeekDays } from './StocksCalendarFormMultipleDaysWeekDays'

function renderStocksCalendarFormMultipleDaysWeekDays(
  defaultFormValues: Partial<StocksCalendarFormValues> = {}
) {
  function StocksCalendarFormMultipleDaysWeekDaysWrapper() {
    const form = useForm<StocksCalendarFormValues>({
      defaultValues: {
        durationType: DurationTypeOption.MULTIPLE_DAYS_WEEKS,
        timeSlotType: TimeSlotTypeOption.SPECIFIC_TIME,
        specificTimeSlots: [{ slot: '' }],
        pricingCategoriesQuantities: [{ isUnlimited: true, priceCategory: '' }],
        oneDayDate: '',
        multipleDaysWeekDays: weekDays.map((d) => ({
          label: d.label,
          value: d.value,
          checked: true,
        })),
        ...defaultFormValues,
      },
    })

    return (
      <FormProvider {...form}>
        <StocksCalendarFormMultipleDaysWeekDays form={form} />
      </FormProvider>
    )
  }

  return renderWithProviders(<StocksCalendarFormMultipleDaysWeekDaysWrapper />)
}

describe('StocksCalendarFormMultipleDaysWeekDays', () => {
  it('should disable all week days that are not within the period', () => {
    const checkedDaysRange = [addDays(new Date(), 1), addDays(new Date(), 3)]
    const checkedWeekDaysIndexes = checkedDaysRange.map((d) => getISODay(d))

    renderStocksCalendarFormMultipleDaysWeekDays({
      multipleDaysStartDate: checkedDaysRange[0].toISOString().split('T')[0],
      multipleDaysEndDate: checkedDaysRange[1].toISOString().split('T')[0],
      multipleDaysWeekDays: weekDays.map((d, i) => ({
        label: d.label,
        value: d.value,
        checked: checkedWeekDaysIndexes.includes(i),
      })),
    })

    expect(
      screen
        .getAllByRole('checkbox')
        .filter((value) => value.hasAttribute('disabled'))
    ).toHaveLength(4)
  })
})
