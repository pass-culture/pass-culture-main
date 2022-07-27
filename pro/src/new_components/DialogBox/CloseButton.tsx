import React from 'react'

import { ReactComponent as CloseDialogIcon } from 'icons/close-dialog.svg'

interface ICloseButtonProps {
  onCloseClick?: () => void
}

const CloseButton = ({ onCloseClick }: ICloseButtonProps): JSX.Element => (
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
