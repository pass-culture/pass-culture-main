import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { AddActivationCodeConfirmationForm } from './AddActivationCodeConfirmationForm'

const LABELS = {
  expirationDate: 'Date de fin de validité *',
}

describe('AddActivationCodeConfirmationForm', () => {
  const today = new Date('2025-09-17T12:00:00Z')
  const minExpirationDate = new Date('2025-09-20T12:00:00Z')

  it('should render confirmation texts and expiration date field', () => {
    renderWithProviders(
      <AddActivationCodeConfirmationForm
        onExpirationDateChange={vi.fn()}
        today={today}
        minExpirationDate={minExpirationDate}
        departmentCode={'75'}
      />
    )

    expect(screen.getByText('Cette opération est irréversible')).toBeTruthy()
    expect(screen.getByLabelText(LABELS.expirationDate)).toBeInTheDocument()
    expect(
      screen.queryByLabelText('Date limite de réservation *')
    ).not.toBeInTheDocument()
  })

  it('should call onExpirationDateChange with normalized date when selected', async () => {
    const onExpirationDateChange = vi.fn()

    renderWithProviders(
      <AddActivationCodeConfirmationForm
        onExpirationDateChange={onExpirationDateChange}
        today={today}
        minExpirationDate={minExpirationDate}
        departmentCode={'75'}
      />
    )

    const dateInput = screen.getByLabelText(LABELS.expirationDate)
    await userEvent.type(dateInput, '2025-10-01')

    expect(onExpirationDateChange).toHaveBeenLastCalledWith('2025-10-01')
  })

  it('should call onExpirationDateChange with undefined when date is cleared', async () => {
    const onExpirationDateChange = vi.fn()

    renderWithProviders(
      <AddActivationCodeConfirmationForm
        onExpirationDateChange={onExpirationDateChange}
        today={today}
        minExpirationDate={minExpirationDate}
        departmentCode={'75'}
      />
    )

    const dateInput = screen.getByLabelText(LABELS.expirationDate)
    await userEvent.type(dateInput, '2025-10-01')
    await userEvent.clear(dateInput)

    expect(onExpirationDateChange).toHaveBeenLastCalledWith(undefined)
  })
})
