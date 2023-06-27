import React from 'react'

import { ReactComponent as StrokeErrorIcon } from 'icons/stroke-error.svg'
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
}: ConfirmDialogProps): JSX.Element => {
  const Icon = icon ?? StrokeErrorIcon

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
