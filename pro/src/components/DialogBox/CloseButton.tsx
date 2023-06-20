import React, { RefObject } from 'react'

import strokeCloseIcon from 'icons/stroke-close.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './DialogBox.module.scss'

interface ICloseButtonProps {
  onCloseClick?: () => void
  ref?: RefObject<HTMLButtonElement> | null
}

const CloseButton = ({ onCloseClick, ref }: ICloseButtonProps): JSX.Element => (
  <button
    className={styles['dialog-box-close']}
    onClick={onCloseClick}
    title="Fermer la modale"
    type="button"
    ref={ref}
  >
    <SvgIcon
      src={strokeCloseIcon}
      alt=""
      className={styles['dialog-box-close-icon']}
    />
  </button>
)

export default CloseButton
