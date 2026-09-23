import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { AddressChangeDialog } from './AddressChangeDialog'

const defaultProps = {
  open: true,
  onOpenChange: vi.fn(),
}

const renderDialog = (props: Partial<typeof defaultProps> = {}) => {
  return renderWithProviders(
    <AddressChangeDialog {...defaultProps} {...props} />
  )
}

describe('AddressChangeDialog', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderDialog({ open: false })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should not display the dialog when closed', () => {
    renderDialog({ open: false })

    expect(
      screen.getByText(/Le changement d.adresse postale/)
    ).not.toBeVisible()
  })

  it('should call onOpenChange(false) when clicking the confirm button', async () => {
    const user = userEvent.setup()
    const onOpenChange = vi.fn()
    renderDialog({ onOpenChange })

    await user.click(screen.getByRole('button', { name: "J'ai compris" }))

    expect(onOpenChange).toHaveBeenCalledWith(false)
  })

  it('should call onOpenChange(false) when clicking the cancel button', async () => {
    const user = userEvent.setup()
    const onOpenChange = vi.fn()
    renderDialog({ onOpenChange })

    const closeBtn = screen.getByLabelText('Fermer la boite de dialogue')
    await user.click(closeBtn)

    expect(onOpenChange).toHaveBeenCalledWith(false)
  })
})
