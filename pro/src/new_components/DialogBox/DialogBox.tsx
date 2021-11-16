import { DialogContent, DialogOverlay } from '@reach/dialog'
import '@reach/dialog/styles.css'
import React from 'react'

import CloseButton from './CloseButton'

interface IDialogProps {
  children: React.ReactNode | React.ReactNode[];
  extraClassNames: string;
  hasCloseButton: boolean;
  labelledBy: string;
  onDismiss?: () => void;
  initialFocusRef: React.RefObject<HTMLButtonElement>;
}

const DialogBox = ({
  children,
  extraClassNames,
  hasCloseButton,
  labelledBy,
  onDismiss,
  initialFocusRef
}: IDialogProps): JSX.Element => (
  <DialogOverlay
    className="dialog-box-overlay"
    initialFocusRef={initialFocusRef}
    onDismiss={onDismiss}
  >
    <DialogContent
      aria-labelledby={labelledBy}
      className="dialog-box-content"
    >
      <section className={extraClassNames}>
        {children}
      </section>
      {hasCloseButton && <CloseButton onCloseClick={onDismiss} />}
    </DialogContent>
  </DialogOverlay>
)
export default DialogBox
