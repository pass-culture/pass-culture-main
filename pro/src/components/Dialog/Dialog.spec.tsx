import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { Dialog } from '@/components/Dialog/Dialog'

describe('Dialog', () => {
  const onCancel = vi.fn()

  function renderDialog(onClose?: () => void) {
    render(
      <Dialog onCancel={onCancel} onClose={onClose} title={'dialog'} open />
    )
  }

  it('should call cancel if no close function present', async () => {
    renderDialog()

    await userEvent.click(screen.getByTestId('dialog-builder-close-button'))
    expect(onCancel).toHaveBeenCalledTimes(1)
  })

  it('should call close function if present', async () => {
    const onClose = vi.fn()
    renderDialog(onClose)

    await userEvent.click(screen.getByTestId('dialog-builder-close-button'))
    expect(onCancel).not.toHaveBeenCalled()
    expect(onClose).toHaveBeenCalledTimes(1)
  })
})
