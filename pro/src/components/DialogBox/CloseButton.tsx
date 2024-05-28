import cn from 'classnames'
import React, { RefObject } from 'react'

import strokeCloseIcon from 'icons/stroke-close.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './DialogBox.module.scss'

interface CloseButtonProps {
  onCloseClick?: () => void
  className?: string
  ref?: RefObject<HTMLButtonElement> | null
}

export const CloseButton = ({
  onCloseClick,
  className,
  ref,
}: CloseButtonProps): JSX.Element => (
  <button
    className={cn(styles['dialog-box-close'], className)}
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
