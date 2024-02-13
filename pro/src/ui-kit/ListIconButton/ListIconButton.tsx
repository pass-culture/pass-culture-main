/* istanbul ignore file : no need to test styled html tag  */
import cn from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'

import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import Tooltip from 'ui-kit/Tooltip'
import { useTooltipProps } from 'ui-kit/Tooltip/useTooltipProps'

import styles from './ListIconButton.module.scss'

interface ListIconButtonProps extends React.HTMLProps<HTMLButtonElement> {
  icon: string
  innerRef?: React.RefObject<HTMLButtonElement>
  className?: string
  tooltipContentClassName?: string
  onClick?: () => void
  url?: string
  isExternal?: boolean
}

const LIST_ICON_SIZE = '16'

const ListIconButton = ({
  children,
  className,
  tooltipContentClassName,
  icon,
  innerRef,
  onClick,
  url,
  isExternal = true,
  ...buttonAttrs
}: ListIconButtonProps): JSX.Element => {
  const { isTooltipHidden, ...tooltipProps } = useTooltipProps(buttonAttrs)

  const svgicon = (
    <SvgIcon
      src={icon}
      alt=""
      className={cn(styles['button-icon'])}
      width={LIST_ICON_SIZE}
    />
  )
  const content = !buttonAttrs?.disabled ? (
    <Tooltip
      content={children}
      tooltipContainerClassName={styles['tooltip']}
      tooltipContentClassName={tooltipContentClassName}
      visuallyHidden={isTooltipHidden}
    >
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
      {...tooltipProps}
    >
      {content}
    </button>
  )

  const link = isExternal ? (
    <a
      className={cn(styles['button'], className)}
      href={url}
      onClick={onClick}
      {...tooltipProps}
    >
      {content}
    </a>
  ) : (
    <Link
      className={cn(styles['button'], className)}
      onClick={onClick}
      to={`${url}`}
      {...tooltipProps}
    >
      {content}
    </Link>
  )

  return url ? link : button
}

export default ListIconButton
