import PropTypes from 'prop-types'
import React from 'react'

import { ReactComponent as CloseDialogIcon } from 'icons/close-dialog.svg'

const CloseButton = ({ onCloseClick }) => (
  <button
    className="dialog-box-close"
    onClick={onCloseClick}
    title="Fermer la modale"
    type="button"
  >
    <CloseDialogIcon />
  </button>
)

CloseButton.propTypes = {
  onCloseClick: PropTypes.func.isRequired,
}

export default CloseButton
