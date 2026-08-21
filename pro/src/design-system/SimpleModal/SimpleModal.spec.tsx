import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createRef } from 'react'
import { axe } from 'vitest-axe'

import * as useMediaQuery from '@/commons/hooks/useMediaQuery'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import fullLinkIcon from '@/icons/full-link.svg'

import { Button } from '../Button/Button'
import { ButtonVariant } from '../Button/types'
import { SimpleModal, type SimpleModalProps } from './SimpleModal'

const renderModalSimple = (props: SimpleModalProps) => {
  return renderWithProviders(<SimpleModal {...props} />)
}

const props: SimpleModalProps = {
  title: 'Modal Title',
  iconPath: fullLinkIcon,
  isOpen: true,
  onClose: vi.fn(),
  children: <p>Modal content.</p>,
  actionButtons: [
    <Button label="Annuler" variant={ButtonVariant.SECONDARY} key="cancel" />,
    <Button label="Confirmer" variant={ButtonVariant.PRIMARY} key="confirm" />,
  ],
}

describe('SimpleModal', () => {
  it('should have an accessible structure', async () => {
    const { container } = renderModalSimple(props)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display the title, children, icon, and buttons', () => {
    renderModalSimple(props)
    expect(screen.getByText('Modal Title')).toBeInTheDocument()
    expect(screen.getByText('Modal content.')).toBeInTheDocument()
    expect(screen.getByTestId('modal-icon')).toBeInTheDocument()
    expect(screen.getByText('Annuler')).toBeInTheDocument()
    expect(screen.getByText('Confirmer')).toBeInTheDocument()
  })

  it('should not display the image when not provided', () => {
    renderModalSimple({
      ...props,
      iconPath: undefined,
    })
    expect(screen.queryByRole('img')).toBeNull()
  })

  it('should call onClose when the modal is closed', async () => {
    const user = userEvent.setup()

    const onCloseMock = vi.fn()
    renderModalSimple({
      ...props,
      isOpen: true,
      onClose: onCloseMock,
    })

    const closeButton = screen.getByLabelText('Fermer la boite de dialogue')
    await user.click(closeButton)

    expect(onCloseMock).toHaveBeenCalled()
  })

  it('should focus refToFocusOnClose when the dialog closes', () => {
    const refToFocusOnClose = createRef<HTMLButtonElement>()
    const { rerender } = renderWithProviders(
      <>
        <button ref={refToFocusOnClose} type="button">
          Outside
        </button>
        <SimpleModal {...props} refToFocusOnClose={refToFocusOnClose} />
      </>
    )

    rerender(
      <>
        <button ref={refToFocusOnClose} type="button">
          Outside
        </button>
        <SimpleModal
          {...props}
          isOpen={false}
          refToFocusOnClose={refToFocusOnClose}
        />
      </>
    )

    expect(screen.getByRole('button', { name: 'Outside' })).toHaveFocus()
  })

  it('should reverse action buttons order on mobile', () => {
    vi.spyOn(useMediaQuery, 'useMediaQuery').mockReturnValueOnce(true)

    const { container } = renderModalSimple(props)
    const actionButtons = container.querySelector('[class*="action-buttons"]')

    expect(actionButtons).not.toBeNull()

    const labels = Array.from(
      actionButtons?.querySelectorAll('button') ?? []
    ).map((button) => button.textContent?.trim())

    expect(labels).toEqual(['Confirmer', 'Annuler'])
  })
})
