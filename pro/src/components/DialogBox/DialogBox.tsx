import '@reach/dialog/styles.css'

import { DialogContent, DialogOverlay } from '@reach/dialog'
import cn from 'classnames'
import React, { FunctionComponent } from 'react'

import CloseButton from './CloseButton'
import styles from './DialogBox.module.scss'

interface DialogProps {
  extraClassNames?: string
  hasCloseButton?: boolean
  labelledBy: string
  onDismiss?: () => void
  initialFocusRef?: React.RefObject<HTMLButtonElement>
  children?: React.ReactNode
  fullContentWidth?: boolean
}

const DialogBox: FunctionComponent<DialogProps> = ({
  children,
  extraClassNames,
  hasCloseButton = false,
  labelledBy,
  onDismiss,
  initialFocusRef,
  fullContentWidth,
}) => (
  <DialogOverlay
    className={styles['dialog-box-overlay']}
    initialFocusRef={initialFocusRef}
    onDismiss={onDismiss}
  >
    <DialogContent
      aria-labelledby={labelledBy}
      className={cn(styles['dialog-box-content'], {
        [styles['dialog-box-full-content-width']]: fullContentWidth,
      })}
    >
      {hasCloseButton && (
        <span className={styles['dialog-box-close-container']}>
          <CloseButton onCloseClick={onDismiss} />
        </span>
      )}
      <section className={extraClassNames}>{children}</section>
    </DialogContent>
  </DialogOverlay>
)
export default DialogBox
