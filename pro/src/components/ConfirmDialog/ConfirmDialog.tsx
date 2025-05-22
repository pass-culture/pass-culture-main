import * as RadixDialog from '@radix-ui/react-dialog'

import strokeErrorIcon from 'icons/stroke-error.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import { Dialog, DialogProps } from '../Dialog/Dialog'

import styles from './ConfirmDialog.module.scss'

type ConfirmDialogProps = DialogProps & {
  onConfirm: () => void
  confirmText: string
  cancelText: string
  isLoading?: boolean
  leftButtonAction?: () => void
  confirmButtonDisabled?: boolean
  open: boolean
}

export const ConfirmDialog = ({
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
  trigger,
  open,
  refToFocusOnClose,
}: ConfirmDialogProps): JSX.Element => {
  const cancelButton = (
    <Button
      onClick={leftButtonAction}
      data-testid="confirm-dialog-button-cancel"
      variant={ButtonVariant.SECONDARY}
    >
      {cancelText}
    </Button>
  )

  const confirmButton = (
    <Button
      onClick={onConfirm}
      isLoading={isLoading}
      disabled={isLoading || confirmButtonDisabled}
      testId="confirm-dialog-button-confirm"
    >
      {confirmText}
    </Button>
  )

  return (
    <Dialog
      onCancel={onCancel}
      title={title}
      secondTitle={secondTitle}
      icon={icon ?? strokeErrorIcon}
      hideIcon={hideIcon}
      explanation={children}
      trigger={trigger}
      extraClassNames={`${extraClassNames} ${styles['confirm-dialog-explanation']}`}
      open={open}
      refToFocusOnClose={refToFocusOnClose}
    >
      <div className={styles['confirm-dialog-actions']}>
        {trigger ? (
          <>
            <RadixDialog.Close asChild>{cancelButton}</RadixDialog.Close>
            <RadixDialog.Close asChild>{confirmButton}</RadixDialog.Close>
          </>
        ) : (
          <>
            {cancelButton}
            {confirmButton}
          </>
        )}
      </div>
    </Dialog>
  )
}
