import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import { renderWithProviders } from 'commons/utils/renderWithProviders'
import {
  DurationTypeOption,
  StocksCalendarFormValues,
  TimeSlotTypeOption,
} from 'components/IndividualOffer/StocksEventCreation/form/types'

import { StocksCalendarFormSpecificTimeSlots } from './StocksCalendarFormSpecificTimeSlots'

function renderStocksCalendarFormSpecificTimeSlots(
  defaultOptions?: Partial<StocksCalendarFormValues>
) {
  function StocksCalendarFormSpecificTimeSlotsWrapper() {
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
        <StocksCalendarFormSpecificTimeSlots form={form} />
      </FormProvider>
    )
  }

  return renderWithProviders(<StocksCalendarFormSpecificTimeSlotsWrapper />)
}

describe('StocksCalendarFormSpecificTimeSlots', () => {
  it('should display a time input for each time slot in the form', () => {
    renderStocksCalendarFormSpecificTimeSlots({
      specificTimeSlots: [
        { slot: '00:00' },
        { slot: '01:00' },
        { slot: '02:00' },
      ],
    })
    expect(screen.getAllByLabelText(/Horaire/)).toHaveLength(3)
  })

  it('should let the user remove a time slot only when there are multiple time slots', async () => {
    renderStocksCalendarFormSpecificTimeSlots({
      specificTimeSlots: [{ slot: '00:00' }],
    })

    expect(
      screen.queryByRole('button', { name: /Supprimer l'horaire/ })
    ).not.toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Ajouter un horaire' })
    )

    expect(
      screen.getAllByRole('button', { name: /Supprimer l'horaire/ })
    ).toHaveLength(2)
  })

  it('should be able to remove a time slot if there are more than one', async () => {
    renderStocksCalendarFormSpecificTimeSlots({
      specificTimeSlots: [{ slot: '00:00' }, { slot: '01:00' }],
    })

    expect(screen.getAllByLabelText(/Horaire/)).toHaveLength(2)

    await userEvent.click(
      screen.getAllByRole('button', { name: /Supprimer l'horaire/ })[0]
    )

    expect(screen.getAllByLabelText(/Horaire/)).toHaveLength(1)
  })
})
