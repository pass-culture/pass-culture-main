import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { UpdateWarningDialog } from './UpdateWarningDialog'

describe('<UpdateWarningDialog />', () => {
  const setup = (message?: string) => {
    const onCancel = vi.fn()
    const onConfirm = vi.fn()
    renderWithProviders(
      <UpdateWarningDialog
        isOpen
        onCancel={onCancel}
        onConfirm={onConfirm}
        message={message}
      />
    )
    return { onCancel, onConfirm }
  }

  it('renders dialog with expected static texts', () => {
    const message = 'Vous avez modifié l’adresse.'
    setup(message)

    expect(
      screen.getByRole('heading', {
        name: /Les changements vont impacter l’ensemble des réservations en cours associées/i,
      })
    ).toBeInTheDocument()

    expect(screen.getByText(message)).toBeInTheDocument()

    expect(
      screen.getByText(/Souhaitez-vous prévenir les jeunes par mail ?/i)
    ).toBeInTheDocument()
  })

  it('calls onCancel when clicking cancel button', async () => {
    const { onCancel } = setup()

    await userEvent.click(screen.getByRole('button', { name: 'Annuler' }))
    expect(onCancel).toHaveBeenCalledTimes(1)
  })

  it('calls onConfirm with true when clicking warn button', async () => {
    const { onConfirm } = setup()

    await userEvent.click(
      screen.getByRole('button', { name: 'Prévenir les jeunes' })
    )
    expect(onConfirm).toHaveBeenCalledWith(true)
  })

  it('calls onConfirm with false after clicking do not warn button', async () => {
    const { onConfirm } = setup()

    await userEvent.click(
      screen.getByRole('button', { name: 'Ne pas prévenir les jeunes' })
    )

    expect(onConfirm).toHaveBeenCalledWith(false)
  })
})
