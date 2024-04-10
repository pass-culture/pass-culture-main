import '@reach/dialog/styles.css'

import { DialogContent, DialogOverlay } from '@reach/dialog'
import cn from 'classnames'
import React, { FunctionComponent } from 'react'

import CloseButton from './CloseButton'
import styles from './DialogBox.module.scss'

interface DialogProps {
  extraClassNames?: string
  closeButtonClassName?: string
  hasCloseButton?: boolean
  labelledBy: string
  onDismiss?: () => void
  children?: React.ReactNode
  fullContentWidth?: boolean
  dangerouslyBypassFocusLock?: boolean
}

const DialogBox: FunctionComponent<DialogProps> = ({
  children,
  extraClassNames,
  closeButtonClassName,
  hasCloseButton = false,
  labelledBy,
  onDismiss,
  fullContentWidth,
  dangerouslyBypassFocusLock = false,
}) => (
  <DialogOverlay
    className={styles['dialog-box-overlay']}
    onDismiss={onDismiss}
    //  The focus lock can be bypassed here to avoid a bug on firefox with the react-focus-lock library used by reach/dialog
    //  https://github.com/reach/reach-ui/issues/615 https://github.com/reach/reach-ui/issues/536
    //  When a new page is opened within an iframe on firefox and the focus is not reset, the focus lock prevents any
    //  input within the dialog to be focused with a mouse click
    dangerouslyBypassFocusLock={dangerouslyBypassFocusLock}
  >
    <DialogContent
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
      <section className={extraClassNames}>{children}</section>
    </DialogContent>
  </DialogOverlay>
)
export default DialogBox
