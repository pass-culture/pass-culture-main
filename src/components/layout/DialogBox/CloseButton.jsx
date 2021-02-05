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

export default CloseButton
