/* istanbul ignore file : no need to test styled html tag  */
import cn from 'classnames'
import React, { useId } from 'react'
import { Link } from 'react-router-dom'

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
  isExternal?: boolean
}

const ListIconButton = ({
  children,
  className,
  icon,
  innerRef,
  hasTooltip,
  onClick,
  url,
  isExternal = true,
  ...buttonAttrs
}: ListIconButtonProps): JSX.Element => {
  const tooltipId = useId()

  const svgicon = (
    <SvgIcon src={icon} alt="" className={cn(styles['button-icon'])} />
  )
  const content =
    hasTooltip && !buttonAttrs?.disabled ? (
      <Tooltip id={tooltipId} content={children} className={styles['tooltip']}>
        {svgicon}
      </Tooltip>
    ) : (
      svgicon
    )

  const button = (
    <button
      className={cn(styles['button'], className)}
      ref={innerRef}
      {...buttonAttrs}
      onClick={onClick}
      type="button"
    >
      {content}
    </button>
  )

  const link = isExternal ? (
    <a className={cn(styles['button'], className)} href={url} onClick={onClick}>
      {content}
    </a>
  ) : (
    <Link className={className} onClick={onClick} to={`${url}`}>
      {content}
    </Link>
  )

  return url ? link : button
}

export default ListIconButton
