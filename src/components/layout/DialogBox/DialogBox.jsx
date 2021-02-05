import { DialogContent, DialogOverlay } from '@reach/dialog'
import '@reach/dialog/styles.css'
import PropTypes from 'prop-types'
import React, { forwardRef } from 'react'

import CloseButton from './CloseButton'

export const DialogBox = forwardRef(function DialogBox(
  { children, extraClassNames, hasCloseButton, labelledBy, onDismiss },
  ref
) {
  return (
    <DialogOverlay
      className="dialog-box-overlay"
      initialFocusRef={ref}
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
})

DialogBox.defaultProps = {
  extraClassNames: '',
  hasCloseButton: false,
}

DialogBox.propTypes = {
  children: PropTypes.oneOfType([PropTypes.arrayOf(PropTypes.element), PropTypes.element])
    .isRequired,
  extraClassNames: PropTypes.string,
  hasCloseButton: PropTypes.bool,
  labelledBy: PropTypes.string.isRequired,
  onDismiss: PropTypes.func.isRequired,
}
