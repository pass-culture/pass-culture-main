import React from 'react'

import strokeErrorIcon from 'icons/stroke-error.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import Dialog, { DialogProps } from '../Dialog'

import styles from './ConfirmDialog.module.scss'

type ConfirmDialogProps = DialogProps & {
  onConfirm: () => void
  confirmText: string
  cancelText: string
  isLoading?: boolean
  leftButtonAction?: () => void
  confirmButtonDisabled?: boolean
}

const ConfirmDialog = ({
  onConfirm,
  onCancel,
  isLoading,
  title,
  secondTitle,
  confirmText,
  cancelText,
  children,
  icon,
  hideIcon = false,
  extraClassNames,
  confirmButtonDisabled = false,
  leftButtonAction = onCancel,
}: ConfirmDialogProps): JSX.Element => {
  return (
    <Dialog
      onCancel={onCancel}
      title={title}
      secondTitle={secondTitle}
      icon={icon ?? strokeErrorIcon}
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
        <Button
          onClick={onConfirm}
          isLoading={isLoading}
          disabled={isLoading || confirmButtonDisabled}
          testId="confirm-dialog-button-confirm"
        >
          {confirmText}
        </Button>
      </div>
    </Dialog>
  )
}

export default ConfirmDialog
