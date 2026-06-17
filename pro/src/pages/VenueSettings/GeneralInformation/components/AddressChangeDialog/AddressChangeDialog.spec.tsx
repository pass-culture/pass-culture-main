import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { AddressChangeDialog } from './AddressChangeDialog'

const defaultProps = {
  open: true,
  onOpenChange: vi.fn(),
}

const renderDialog = (props: Partial<typeof defaultProps> = {}) => {
  renderWithProviders(<AddressChangeDialog {...defaultProps} {...props} />)
}

describe('AddressChangeDialog', () => {
  it('should not display the dialog when closed', () => {
    renderDialog({ open: false })

    expect(
      screen.queryByText(/Le changement d.adresse postale/)
    ).not.toBeInTheDocument()
  })

  it('should call onOpenChange(false) when clicking the confirm button', async () => {
    const onOpenChange = vi.fn()
    renderDialog({ onOpenChange })

    await userEvent.click(screen.getByRole('button', { name: "J'ai compris" }))

    expect(onOpenChange).toHaveBeenCalledWith(false)
  })

  it('should call onOpenChange(false) when clicking the cancel button', async () => {
    const onOpenChange = vi.fn()
    renderDialog({ onOpenChange })

    const closeBtn = screen.getByTestId('dialog-builder-close-button')
    await userEvent.click(closeBtn)

    expect(onOpenChange).toHaveBeenCalledWith(false)
  })
})
