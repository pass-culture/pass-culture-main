import React, { RefObject } from 'react'

import { ReactComponent as CloseDialogIcon } from 'icons/close-dialog.svg'

interface ICloseButtonProps {
  onCloseClick?: () => void
  ref?: RefObject<HTMLButtonElement> | null
}

const CloseButton = ({ onCloseClick, ref }: ICloseButtonProps): JSX.Element => (
  <button
    className="dialog-box-close"
    onClick={onCloseClick}
    title="Fermer la modale"
    type="button"
    ref={ref}
  >
    <CloseDialogIcon />
  </button>
)

export default CloseButton
