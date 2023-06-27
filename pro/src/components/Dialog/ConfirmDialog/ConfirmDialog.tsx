import React from 'react'

import AlertSvg from 'icons/ico-alert-grey.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import Dialog, { IDialogProps } from '../Dialog'

import styles from './ConfirmDialog.module.scss'

type IConfirmDialogProps = IDialogProps & {
  onConfirm: () => void
  confirmText: string
  cancelText: string
  isLoading?: boolean
  leftButtonAction?: () => void
}

const ConfirmDialog = ({
  onConfirm,
  onCancel,
  title,
  secondTitle,
  confirmText,
  cancelText,
  children,
  icon,
  hideIcon = false,
  extraClassNames,
  leftButtonAction = onCancel,
}: IConfirmDialogProps): JSX.Element => {
  const Icon = icon ?? AlertSvg

  return (
    <Dialog
      onCancel={onCancel}
      title={title}
      secondTitle={secondTitle}
      icon={Icon}
      hideIcon={hideIcon}
      explanation={children}
      extraClassNames={`${extraClassNames} ${styles['confirm-dialog-explanation']}`}
    >
      <div className={styles['confirm-dialog-actions']}>
        <Button
          onClick={leftButtonAction}
          data-testid="confirm-dialog-button-cancel"
          variant={ButtonVariant.SECONDARY}
        >
          {cancelText}
        </Button>
        <Button onClick={onConfirm} testId="confirm-dialog-button-confirm">
          {confirmText}
        </Button>
      </div>
    </Dialog>
  )
}

export default ConfirmDialog
