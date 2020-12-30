import { DialogContent, DialogOverlay } from '@reach/dialog'
import PropTypes from 'prop-types'
import React, { forwardRef } from 'react'
import '@reach/dialog/styles.css'

export const DialogBox = forwardRef(function DialogBox(
  { children, extraClassNames, isOpen, labelledBy, onDismiss },
  ref
) {
  return (
    <DialogOverlay
      className="dialog-box-overlay"
      initialFocusRef={ref}
      isOpen={isOpen}
      onDismiss={onDismiss}
    >
      <DialogContent
        aria-labelledby={labelledBy}
        className={`dialog-box-content ${extraClassNames}`}
      >
        {children}
      </DialogContent>
    </DialogOverlay>
  )
})

DialogBox.defaultProps = {
  extraClassNames: '',
  isOpen: true,
}

DialogBox.propTypes = {
  children: PropTypes.arrayOf(PropTypes.element).isRequired,
  extraClassNames: PropTypes.string,
  isOpen: PropTypes.bool,
  labelledBy: PropTypes.string.isRequired,
  onDismiss: PropTypes.func.isRequired,
}
