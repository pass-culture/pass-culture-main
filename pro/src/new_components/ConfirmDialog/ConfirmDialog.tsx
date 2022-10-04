import React from 'react'

import { ReactComponent as AlertSvg } from 'icons/ico-alert-grey.svg'
import DialogBox from 'new_components/DialogBox/DialogBox'
import { Button, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './ConfirmDialog.module.scss'

interface IConfirmDialogProps {
  onConfirm: () => void
  onCancel: () => void
  title: string
  secondTitle?: string
  confirmText: string
  cancelText: string
  isLoading?: boolean
  children: React.ReactNode | React.ReactNode[]
  icon?: React.FunctionComponent<React.SVGProps<SVGSVGElement>>
  hideIcon?: boolean
  extraClassNames?: string
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
}: IConfirmDialogProps): JSX.Element => {
  const Icon = icon ?? AlertSvg

  return (
    <DialogBox
      extraClassNames={`${styles['confirm-dialog']} ${extraClassNames}`}
      hasCloseButton
      labelledBy={title}
      onDismiss={onCancel}
    >
      {!hideIcon && <Icon className={styles['confirm-dialog-icon']} />}
      <div className={styles['confirm-dialog-title']}>
        <strong>{title}</strong>
        <strong>{secondTitle}</strong>
      </div>
      <div className={styles['confirm-dialog-explanation']}>{children}</div>
      <div className={styles['confirm-dialog-actions']}>
        <Button
          className="secondary-button"
          onClick={onCancel}
          type="submit"
          data-testid="confirm-dialog-button-cancel"
          variant={ButtonVariant.SECONDARY}
        >
          {cancelText}
        </Button>
        <SubmitButton
          className="primary-button"
          isLoading={isLoading}
          onClick={onConfirm}
          testId="confirm-dialog-button-confirm"
        >
          {confirmText}
        </SubmitButton>
      </div>
    </DialogBox>
  )
}

export default ConfirmDialog
