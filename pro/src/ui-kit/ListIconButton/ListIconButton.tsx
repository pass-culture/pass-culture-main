/* istanbul ignore file : no need to test styled html tag  */
import cn from 'classnames'
import React, { MouseEvent, forwardRef, ForwardedRef } from 'react'
import { Link } from 'react-router-dom'

import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tooltip } from 'ui-kit/Tooltip/Tooltip'
import { useTooltipProps } from 'ui-kit/Tooltip/useTooltipProps'

import styles from './ListIconButton.module.scss'

export enum ListIconButtonVariant {
  DEFAULT = 'default',
  PRIMARY = 'primary',
}

interface ListIconButtonProps extends React.HTMLProps<HTMLButtonElement> {
  icon: string
  variant?: ListIconButtonVariant
  className?: string
  tooltipContentClassName?: string
  onClick?: (event: MouseEvent) => void
  url?: string
  isExternal?: boolean
  dataTestid?: string
}

const LIST_ICON_SIZE = '16'

export const ListIconButton = forwardRef(
  (
    {
      children,
      className,
      variant = ListIconButtonVariant.DEFAULT,
      tooltipContentClassName,
      icon,
      onClick,
      url,
      isExternal = true,
      dataTestid,
      ...buttonAttrs
    }: ListIconButtonProps,
    forwadedRef: ForwardedRef<HTMLButtonElement>
  ): JSX.Element => {
    const { isTooltipHidden, ...tooltipProps } = useTooltipProps(buttonAttrs)

    const svgicon = (
      <SvgIcon
        src={icon}
        alt=""
        className={cn(styles['button-icon'])}
        width={LIST_ICON_SIZE}
      />
    )
    const content = !buttonAttrs.disabled ? (
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
        className={cn(
          styles['button'],
          styles[`variant-${variant}`],
          className
        )}
        ref={forwadedRef}
        {...buttonAttrs}
        onClick={onClick}
        type="button"
        data-testid={dataTestid}
        {...tooltipProps}
      >
        {content}
      </button>
    )

    const link = isExternal ? (
      <a
        className={cn(
          styles['button'],
          styles[`variant-${variant}`],
          className
        )}
        href={url}
        onClick={onClick}
        {...tooltipProps}
      >
        {content}
      </a>
    ) : (
      <Link
        className={cn(
          styles['button'],
          styles[`variant-${variant}`],
          className
        )}
        onClick={onClick}
        to={`${url}`}
        {...tooltipProps}
      >
        {content}
      </Link>
    )

    return url ? link : button
  }
)

ListIconButton.displayName = 'ListIconButton'
