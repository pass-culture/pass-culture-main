import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import type { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OpeningHours } from './OpeningHours'

const DEFAULT_OPENING_HOURS: WeekdayOpeningHoursTimespans = {
  MONDAY: [
    ['10:10', '11:11'],
    ['12:12', '13:13'],
  ],
  TUESDAY: [
    ['15:10', '16:11'],
    ['18:12', '22:13'],
  ],
  WEDNESDAY: null,
  THURSDAY: [['10:10', '11:11']],
  FRIDAY: null,
  SATURDAY: null,
  SUNDAY: null,
}

function renderOpeningHours(
  initialValues: Partial<{
    openingHours: WeekdayOpeningHoursTimespans | null
  }> = { openingHours: DEFAULT_OPENING_HOURS }
) {
  function OpeningHoursFormWrapper() {
    const form = useForm({
      defaultValues: {
        ...initialValues,
      },
    })

    return (
      <FormProvider {...form}>
        <OpeningHours />
      </FormProvider>
    )
  }

  return renderWithProviders(<OpeningHoursFormWrapper />)
}

describe('OpeningHours', () => {
  it('should show a group for each day of the week', () => {
    renderOpeningHours()

    expect(screen.getByRole('group', { name: 'Lundi' })).toBeInTheDocument()
    expect(screen.getByRole('group', { name: 'Mercredi' })).toBeInTheDocument()
    expect(screen.getAllByRole('group')).toHaveLength(7)
  })

  it('should show a date input for each timespan', () => {
    renderOpeningHours()

    expect(screen.getAllByLabelText(/Ouvre à */)).toHaveLength(5)
    expect(screen.getAllByLabelText(/Ferme à */)).toHaveLength(5)
  })

  it('should add a start and end timespans when clicking on the "Ajouter une plage horaire" button', async () => {
    renderOpeningHours({
      openingHours: { MONDAY: [['10:10', '11:11']] },
    })

    expect(screen.getAllByLabelText(/Ouvre à */)).toHaveLength(1)
    expect(screen.getAllByLabelText(/Ferme à */)).toHaveLength(1)

    await userEvent.click(
      screen.getByRole('button', { name: 'Ajouter une plage horaire le lundi' })
    )

    expect(screen.getAllByLabelText(/Ouvre à */)).toHaveLength(2)
    expect(screen.getAllByLabelText(/Ferme à */)).toHaveLength(2)
  })

  it('should remove a start and end timespans when clicking on the "Supprimer la plage horaire" button', async () => {
    renderOpeningHours({
      openingHours: {
        MONDAY: [
          ['10:10', '11:11'],
          ['12:12', '13:13'],
        ],
      },
    })

    expect(screen.getAllByLabelText(/Ouvre à */)).toHaveLength(2)
    expect(screen.getAllByLabelText(/Ferme à */)).toHaveLength(2)

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Supprimer la deuxième plage horaire du lundi',
      })
    )

    expect(screen.getAllByLabelText(/Ouvre à */)).toHaveLength(1)
    expect(screen.getAllByLabelText(/Ferme à */)).toHaveLength(1)
  })

  it('should show that the day is closed when there are no opening hours for the day', () => {
    renderOpeningHours()

    expect(screen.getAllByText('Fermé')).toHaveLength(4)
  })
})
