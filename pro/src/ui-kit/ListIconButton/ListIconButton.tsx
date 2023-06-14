/* istanbul ignore file : no need to test styled html tag  */
import cn from 'classnames'
import React, { useId } from 'react'

import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import Tooltip from 'ui-kit/Tooltip'

import styles from './ListIconButton.module.scss'

export interface ListIconButtonProps
  extends React.HTMLProps<HTMLButtonElement> {
  icon: string
  innerRef?: React.RefObject<HTMLButtonElement>
  className?: string
  hasTooltip?: boolean
  onClick?: () => void
  url?: string
}

const ListIconButton = ({
  children,
  className,
  icon,
  innerRef,
  hasTooltip,
  onClick,
  url,
  ...buttonAttrs
}: ListIconButtonProps): JSX.Element => {
  const tooltipId = useId()
  const button = (
    <button
      className={cn(styles['button'], className)}
      ref={innerRef}
      {...buttonAttrs}
      onClick={onClick}
      type="button"
    >
      <SvgIcon src={icon} alt="" className={cn(styles['button-icon'])} />
      <div className={styles['visually-hidden']}>{children}</div>
    </button>
  )
  const link = (
    <a className={cn(styles['button'], className)} href={url} onClick={onClick}>
      <SvgIcon src={icon} alt="" className={cn(styles['button-icon'])} />
      <div className={styles['visually-hidden']}>{children}</div>
    </a>
  )
  if (hasTooltip && !buttonAttrs?.disabled) {
    return (
      <Tooltip id={tooltipId} content={children} className={styles['tooltip']}>
        {url ? link : button}
      </Tooltip>
    )
  }
  return button
}

export default ListIconButton
