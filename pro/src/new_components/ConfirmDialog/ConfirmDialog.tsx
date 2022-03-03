import React, { useRef } from 'react'

import { ReactComponent as AlertSvg } from 'icons/ico-alert-grey.svg'
import DialogBox from 'new_components/DialogBox/DialogBox'
import { SubmitButton } from 'ui-kit'

import styles from './ConfirmDialog.module.scss'

interface IConfirmDialogProps {
  onConfirm: () => void
  onCancel: () => void
  title: string
  confirmText: string
  cancelText: string
  isLoading?: boolean
  children: React.ReactNode | React.ReactNode[]
}

const ConfirmDialog = ({
  onConfirm,
  onCancel,
  title,
  confirmText,
  cancelText,
  isLoading = false,
  children,
}: IConfirmDialogProps): JSX.Element => {
  const buttonRef = useRef<HTMLButtonElement | null>(null)

  return (
    <DialogBox
      extraClassNames={styles['confirm-dialog']}
      hasCloseButton={false}
      initialFocusRef={buttonRef}
      labelledBy={title}
    >
      <AlertSvg className={styles['confirm-dialog-icon']} />
      <div className={styles['confirm-dialog-title']}>
        <strong>{title}</strong>
      </div>
      <div className={styles['confirm-dialog-explanation']}>{children}</div>
      <div className={styles['confirm-dialog-actions']}>
        <button className="secondary-button" onClick={onCancel} type="submit">
          {cancelText}
        </button>
        <SubmitButton
          className="primary-button"
          isLoading={isLoading}
          onClick={onConfirm}
          ref={buttonRef}
        >
          {confirmText}
        </SubmitButton>
      </div>
    </DialogBox>
  )
}

export default ConfirmDialog
