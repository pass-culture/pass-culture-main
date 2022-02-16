import React, { FunctionComponent, SVGProps, useState } from 'react'
import Modal from 'react-modal'

import Button from 'app/ui-kit/Button'
import { ReactComponent as Logo } from 'assets/logo-without-text.svg'

import './ModalLayout.scss'

interface IModalLayout {
  closeModal: () => void
  isOpen: boolean
  action?: () => Promise<void>
  actionLabel?: string
  children: React.ReactNode | React.ReactNode[]
  Icon?: FunctionComponent<
    SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
}
const ModalLayout = ({
  closeModal,
  isOpen,
  action,
  actionLabel,
  children,
  Icon,
}: IModalLayout): JSX.Element => {
  const [isLoading, setIsLoading] = useState(false)

  const handleButtonClick = async () => {
    if (action) {
      setIsLoading(true)
      await action()
      setIsLoading(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      style={{
        content: {
          width: '452px',
          height: 'fit-content',
          margin: 'auto',
          padding: '48px 48px 24px',
          boxSizing: 'border-box',
          fontSize: '15px',
          borderRadius: '10px',
        },
        overlay: {
          backgroundColor: 'rgba(0, 0, 0, 0.4)',
        },
      }}
    >
      {Icon ? <Icon className="modal-logo" /> : <Logo className="modal-logo" />}
      {children}
      <div className="modal-buttons">
        <Button
          className="modal-button"
          label="Fermer"
          onClick={closeModal}
          variant={actionLabel ? 'secondary' : 'primary'}
        />
        {actionLabel && (
          <Button
            className="modal-button"
            isLoading={isLoading}
            label={actionLabel}
            onClick={handleButtonClick}
          />
        )}
      </div>
    </Modal>
  )
}

export default ModalLayout
