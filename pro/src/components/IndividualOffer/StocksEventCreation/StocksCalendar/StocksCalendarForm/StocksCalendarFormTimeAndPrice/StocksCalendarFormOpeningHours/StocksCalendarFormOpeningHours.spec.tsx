import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import { renderWithProviders } from 'commons/utils/renderWithProviders'
import {
  DurationTypeOption,
  StocksCalendarFormValues,
  TimeSlotTypeOption,
} from 'components/IndividualOffer/StocksEventCreation/form/types'

import { StocksCalendarFormOpeningHours } from './StocksCalendarFormOpeningHours'

function renderStocksCalendarFormOpeningHours(
  values?: Partial<StocksCalendarFormValues>
) {
  function StocksCalendarFormOpeningHoursWrapper() {
    const form = useForm<StocksCalendarFormValues>({
      defaultValues: {
        durationType: DurationTypeOption.MULTIPLE_DAYS_WEEKS,
        timeSlotType: TimeSlotTypeOption.OPENING_HOURS,
        specificTimeSlots: [{ slot: '' }],
        pricingCategoriesQuantities: [{ isUnlimited: true, priceCategory: '' }],
        oneDayDate: '',
        openingHours: {
          MONDAY: [{ open: '00:00', close: '00:00' }],
          TUESDAY: [{ open: '00:00', close: '00:00' }],
        },
        ...values,
      },
    })

    return (
      <FormProvider {...form}>
        <StocksCalendarFormOpeningHours form={form} />
      </FormProvider>
    )
  }

  return renderWithProviders(<StocksCalendarFormOpeningHoursWrapper />)
}

describe('StocksCalendarFormOpeningHours', () => {
  it('should display opening and closing inputs for selected week days', () => {
    renderStocksCalendarFormOpeningHours()

    expect(screen.getByRole('group', { name: 'Lundi' })).toBeInTheDocument()

    expect(screen.getAllByLabelText('Ouvre à')).toHaveLength(2)
    expect(screen.getAllByLabelText('Ferme à')).toHaveLength(2)
  })

  it('should be able to add and remove time slots for a specific week day', async () => {
    renderStocksCalendarFormOpeningHours({
      openingHours: { MONDAY: [{ open: '00:00', close: '00:00' }] },
    })

    expect(screen.getAllByLabelText('Ouvre à')).toHaveLength(1)
    expect(screen.getAllByLabelText('Ferme à')).toHaveLength(1)

    await userEvent.click(
      screen.getByRole('button', { name: 'Ajouter une plage horaire' })
    )

    expect(screen.getAllByLabelText('Ouvre à')).toHaveLength(2)
    expect(screen.getAllByLabelText('Ferme à')).toHaveLength(2)

    await userEvent.click(
      screen.getByRole('button', { name: 'Supprimer la plage horaire' })
    )

    expect(screen.getAllByLabelText('Ouvre à')).toHaveLength(1)
    expect(screen.getAllByLabelText('Ferme à')).toHaveLength(1)
  })
})
