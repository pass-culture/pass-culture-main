import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

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
  actionButtons: (
    <>
      <Button label="Annuler" variant={ButtonVariant.SECONDARY} />
      <Button label="Confirmer" variant={ButtonVariant.PRIMARY} />
    </>
  ),
}

describe('SimpleModal', () => {
  beforeEach(() => {
    HTMLDialogElement.prototype.showModal = vi.fn()
    HTMLDialogElement.prototype.close = vi.fn()
  })

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

  it('should call onClose when the modal is closed', () => {
    const onCloseMock = vi.fn()
    renderModalSimple({
      ...props,
      isOpen: true,
      onClose: onCloseMock,
    })

    const closeButton = screen.getByLabelText('Fermer la boite de dialogue')
    closeButton.click()

    expect(onCloseMock).toHaveBeenCalled()
  })
})
