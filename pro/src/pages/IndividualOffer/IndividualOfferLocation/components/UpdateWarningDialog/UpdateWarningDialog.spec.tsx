import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { UpdateWarningDialog } from './UpdateWarningDialog'

describe('<UpdateWarningDialog />', () => {
  const setup = () => {
    const onCancel = vi.fn()
    const onConfirm = vi.fn()
    renderWithProviders(
      <UpdateWarningDialog onCancel={onCancel} onConfirm={onConfirm} />
    )
    return { onCancel, onConfirm }
  }

  it('renders dialog with expected static texts and checkbox checked by default', () => {
    setup()

    expect(
      screen.getByRole('heading', {
        name: /Les changements vont s’appliquer à l’ensemble des réservations en cours associées/i,
      })
    ).toBeInTheDocument()

    expect(
      screen.getByText(/Vous avez modifié la localisation\./i)
    ).toBeInTheDocument()

    expect(
      screen.getByText(
        /Pour conserver les données des réservations actuelles, créez une nouvelle offre avec vos modifications/i
      )
    ).toBeInTheDocument()

    const checkbox = screen.getByRole('checkbox', {
      name: /Prévenir les jeunes par e-mail/i,
    }) as HTMLInputElement
    expect(checkbox.checked).toBe(true)
  })

  it('calls onCancel when clicking cancel button', async () => {
    const { onCancel } = setup()

    await userEvent.click(screen.getByTestId('confirm-dialog-button-cancel'))
    expect(onCancel).toHaveBeenCalledTimes(1)
  })

  it('calls onConfirm with true when checkbox left checked', async () => {
    const { onConfirm } = setup()

    await userEvent.click(screen.getByTestId('confirm-dialog-button-confirm'))
    expect(onConfirm).toHaveBeenCalledWith(true)
  })

  it('calls onConfirm with false after unchecking the mail checkbox', async () => {
    const { onConfirm } = setup()

    const checkbox = screen.getByRole('checkbox', {
      name: /Prévenir les jeunes par e-mail/i,
    })
    await userEvent.click(checkbox) // uncheck

    expect((checkbox as HTMLInputElement).checked).toBe(false)

    await userEvent.click(screen.getByTestId('confirm-dialog-button-confirm'))
    expect(onConfirm).toHaveBeenCalledWith(false)
  })
})
