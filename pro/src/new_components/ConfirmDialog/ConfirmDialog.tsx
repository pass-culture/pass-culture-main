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
  icon?: React.FunctionComponent<React.SVGProps<SVGSVGElement>>
}

const ConfirmDialog = ({
  onConfirm,
  onCancel,
  title,
  confirmText,
  cancelText,
  isLoading = false,
  children,
  icon,
}: IConfirmDialogProps): JSX.Element => {
  const buttonRef = useRef<HTMLButtonElement | null>(null)

  const Icon = icon ?? AlertSvg

  return (
    <DialogBox
      extraClassNames={styles['confirm-dialog']}
      hasCloseButton
      initialFocusRef={buttonRef}
      labelledBy={title}
      onDismiss={onCancel}
    >
      <Icon className={styles['confirm-dialog-icon']} />
      <div className={styles['confirm-dialog-title']}>
        <strong>{title}</strong>
      </div>
      <div className={styles['confirm-dialog-explanation']}>{children}</div>
      <div className={styles['confirm-dialog-actions']}>
        <button className="secondary-button" onClick={onCancel} type="submit">
          {cancelText}
        </button>
        <SubmitButton
          buttonRef={buttonRef}
          className="primary-button"
          isLoading={isLoading}
          onClick={onConfirm}
        >
          {confirmText}
        </SubmitButton>
      </div>
    </DialogBox>
  )
}

export default ConfirmDialog
