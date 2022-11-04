import '@reach/dialog/styles.css'

import { DialogContent, DialogOverlay } from '@reach/dialog'
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
}

const DialogBox: FunctionComponent<DialogProps> = ({
  children,
  extraClassNames,
  hasCloseButton = false,
  labelledBy,
  onDismiss,
  initialFocusRef,
}) => (
  <DialogOverlay
    className="dialog-box-overlay"
    initialFocusRef={initialFocusRef}
    onDismiss={onDismiss}
  >
    <DialogContent aria-labelledby={labelledBy} className="dialog-box-content">
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
