import { ReactComponent as CloseDialogIcon } from 'icons/close-dialog.svg'
import React from 'react'

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
