import * as RadixDialog from '@radix-ui/react-dialog'

import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import strokeErrorIcon from '@/icons/stroke-error.svg'

import { Dialog, type DialogProps } from '../Dialog/Dialog'
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
  onClose,
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
      variant={ButtonVariant.SECONDARY}
      color={
        // That's a Design-System rule for secondary buttons
        ['annuler', 'annuler et quitter', 'fermer'].includes(
          cancelText.toLowerCase()
        )
          ? ButtonColor.NEUTRAL
          : ButtonColor.BRAND
      }
      label={cancelText}
    />
  )

  const confirmButton = (
    <Button
      onClick={onConfirm}
      isLoading={isLoading}
      disabled={isLoading || confirmButtonDisabled}
      label={confirmText}
      data-testid="confirm-dialog-button-confirm"
    />
  )

  return (
    <Dialog
      onCancel={onCancel}
      onClose={onClose}
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
