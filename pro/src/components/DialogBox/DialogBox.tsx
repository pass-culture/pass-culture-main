import * as Dialog from '@radix-ui/react-dialog'
import cn from 'classnames'
import React, { FunctionComponent } from 'react'

import { CloseButton } from './CloseButton'
import styles from './DialogBox.module.scss'

interface DialogProps {
  extraClassNames?: string
  closeButtonClassName?: string
  hasCloseButton?: boolean
  labelledBy: string
  onDismiss?: () => void
  children?: React.ReactNode
  fullContentWidth?: boolean
}

export const DialogBox: FunctionComponent<DialogProps> = ({
  children,
  extraClassNames,
  closeButtonClassName,
  hasCloseButton = false,
  labelledBy,
  onDismiss,
  fullContentWidth,
}) => (
  <Dialog.Root
    defaultOpen
    onOpenChange={(open) => {
      if (!open && onDismiss) {
        onDismiss()
      }
    }}
  >
    <Dialog.Portal>
      <Dialog.Overlay className={styles['dialog-box-overlay']}>
        <Dialog.Content
          aria-labelledby={labelledBy}
          className={cn(styles['dialog-box-content'], {
            [styles['dialog-box-full-content-width']]: fullContentWidth,
          })}
        >
          {hasCloseButton && (
            <div className={styles['dialog-box-close-container']}>
              <CloseButton
                onCloseClick={onDismiss}
                className={closeButtonClassName}
              />
            </div>
          )}
          <Dialog.Description asChild>
            <section className={extraClassNames}>{children}</section>
          </Dialog.Description>
        </Dialog.Content>
      </Dialog.Overlay>
    </Dialog.Portal>
  </Dialog.Root>
)
