import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import ConfirmDialog from '..'

describe('ConfirmDialog', () => {
  const onConfirm = vi.fn()
  const onCancel = vi.fn()

  it('should call onConfirm on confirm button click', async () => {
    render(
      <ConfirmDialog
        title="Dialog"
        onConfirm={onConfirm}
        onCancel={onCancel}
        confirmText="Valider"
        cancelText="Annuler"
      />
    )

    await userEvent.click(screen.getByText('Valider'))
    expect(onConfirm).toHaveBeenCalledTimes(1)
  })

  it('should call onCancel on cancel button click', async () => {
    render(
      <ConfirmDialog
        title="Dialog"
        onConfirm={onConfirm}
        onCancel={onCancel}
        confirmText="Valider"
        cancelText="Annuler"
      />
    )

    await userEvent.click(screen.getByText('Annuler'))
    expect(onCancel).toHaveBeenCalledTimes(1)
  })
})
