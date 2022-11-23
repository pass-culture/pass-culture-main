import React from 'react'

import { ReactComponent as AlertSvg } from 'icons/ico-alert-grey.svg'
import { Button, SubmitButton } from 'ui-kit'
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
  isLoading = false,
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
          type="submit"
          data-testid="confirm-dialog-button-cancel"
          variant={ButtonVariant.SECONDARY}
        >
          {cancelText}
        </Button>
        <SubmitButton
          isLoading={isLoading}
          onClick={onConfirm}
          testId="confirm-dialog-button-confirm"
        >
          {confirmText}
        </SubmitButton>
      </div>
    </Dialog>
  )
}

export default ConfirmDialog
