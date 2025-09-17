import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { AddActivationCodeConfirmationForm } from './AddActivationCodeConfirmationForm'

const LABELS = {
  date: 'Date limite de validité',
  validate: 'Valider',
  back: 'Retour',
}

describe('AddActivationCodeConfirmationForm', () => {
  const today = new Date('2025-09-17T12:00:00Z')
  const minExpirationDate = new Date('2025-09-20T12:00:00Z')

  it('should render confirmation text with number of codes', () => {
    renderWithProviders(
      <AddActivationCodeConfirmationForm
        unsavedActivationCodes={['A', 'B', 'C']}
        clearActivationCodes={vi.fn()}
        submitActivationCodes={vi.fn()}
        today={today}
        minExpirationDate={minExpirationDate}
        departmentCode={'75'}
      />
    )

    expect(
      screen.getByText(/Vous êtes sur le point d’ajouter 3 codes d’activation./)
    ).toBeInTheDocument()
  })

  it('should call clearActivationCodes on Retour click', async () => {
    const clearActivationCodes = vi.fn()

    renderWithProviders(
      <AddActivationCodeConfirmationForm
        unsavedActivationCodes={['A']}
        clearActivationCodes={clearActivationCodes}
        submitActivationCodes={vi.fn()}
        today={today}
        minExpirationDate={null}
        departmentCode={'75'}
      />
    )

    await userEvent.click(screen.getByRole('button', { name: LABELS.back }))

    expect(clearActivationCodes).toHaveBeenCalledTimes(1)
  })

  it('should submit without expiration date if none chosen', async () => {
    const submitActivationCodes = vi.fn()

    renderWithProviders(
      <AddActivationCodeConfirmationForm
        unsavedActivationCodes={['A']}
        clearActivationCodes={vi.fn()}
        submitActivationCodes={submitActivationCodes}
        today={today}
        minExpirationDate={null}
        departmentCode={'75'}
      />
    )

    await userEvent.click(screen.getByRole('button', { name: LABELS.validate }))

    expect(submitActivationCodes).toHaveBeenCalledWith(undefined)
  })

  it('should set expiration date and submit it when selected', async () => {
    const submitActivationCodes = vi.fn()

    renderWithProviders(
      <AddActivationCodeConfirmationForm
        unsavedActivationCodes={['A', 'B']}
        clearActivationCodes={vi.fn()}
        submitActivationCodes={submitActivationCodes}
        today={today}
        minExpirationDate={minExpirationDate}
        departmentCode={'75'}
      />
    )

    const dateInput = screen.getByLabelText(LABELS.date)
    await userEvent.type(dateInput, '2025-10-01')
    await userEvent.click(screen.getByRole('button', { name: LABELS.validate }))

    // formatShortDateForInput + timezone conversion will produce same YYYY-MM-DD here due to mock date
    expect(submitActivationCodes).toHaveBeenCalledWith('2025-10-01')
  })
})
