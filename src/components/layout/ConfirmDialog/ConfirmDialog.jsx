import PropTypes from "prop-types"
import React from 'react'

import { DialogBox } from "components/layout/DialogBox/DialogBox"
import { ReactComponent as AlertSvg } from "icons/ico-alert-grey.svg"
import './_ConfirmDialog.scss'

const ConfirmDialog = ({
  onConfirm,
  onCancel,
  title,
  confirmText,
  cancelText,
  children  }) => {
  return (
    <DialogBox extraClassNames="provider-import-confirmation-dialog">
      <AlertSvg />
      <div className="title">
        <strong>
          {title}
        </strong>
      </div>
      <div className="explanation">
        {children}
      </div>
      <div className="actions">
        <button
          className="secondary-button"
          onClick={onCancel}
          type="submit"
        >
          {cancelText}
        </button>
        <button
          className="primary-button confirm"
          onClick={onConfirm}
          type="button"
        >
          {confirmText}
        </button>
      </div>
    </DialogBox>
  )
}

ConfirmDialog.defaultProps = {
  children: null,
}

ConfirmDialog.propTypes = {
  cancelText: PropTypes.string.isRequired,
  children: PropTypes.node,
  confirmText: PropTypes.string.isRequired,
  onCancel: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
}

export default ConfirmDialog
