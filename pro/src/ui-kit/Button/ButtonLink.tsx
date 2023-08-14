import cn from 'classnames'
import React, { MouseEventHandler, useId } from 'react'
import { Link } from 'react-router-dom'

import fullRightIcon from 'icons/full-right.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import Tooltip from 'ui-kit/Tooltip'

import styles from './Button.module.scss'
import { ButtonVariant, IconPositionEnum, SharedButtonProps } from './types'

export type LinkProps = {
  isExternal: boolean
  to: string
  rel?: string
  target?: string
  'aria-label'?: string
  type?: string
  download?: boolean
}

export interface ButtonLinkProps extends SharedButtonProps {
  link: LinkProps
  children?: React.ReactNode | React.ReactNode[]
  className?: string
  isDisabled?: boolean
  onClick?: MouseEventHandler<HTMLAnchorElement>
  hasTooltip?: boolean
  svgAlt?: string
}

const ButtonLink = ({
  className,
  children,
  icon,
  isDisabled = false,
  onClick,
  variant = ButtonVariant.TERNARY,
  link,
  iconPosition = IconPositionEnum.LEFT,
  hasTooltip = false,
  svgAlt = '',
}: ButtonLinkProps): JSX.Element => {
  const classNames = cn(
    styles['button'],
    styles[`button-${variant}`],
    styles[`button-${iconPosition}`],
    { [styles[`button-disabled`]]: isDisabled },
    className
  )

  let body = (
    <>
      {
        /* istanbul ignore next: graphic variation */
        icon && iconPosition !== IconPositionEnum.RIGHT && (
          <SvgIcon
            src={icon}
            alt={svgAlt}
            className={styles['button-icon']}
            width="22"
          />
        )
      }
      {hasTooltip ? (
        <div className={styles['visually-hidden']}>{children}</div>
      ) : /* istanbul ignore next: graphic variation */ variant ===
        ButtonVariant.BOX ? (
        <div className={styles['button-arrow-content']}>{children}</div>
      ) : (
        children
      )}
      {
        /* istanbul ignore next: graphic variation */
        icon && iconPosition === IconPositionEnum.RIGHT && (
          <SvgIcon
            src={icon}
            alt={svgAlt}
            className={styles['button-icon']}
            width="22"
          />
        )
      }
      {
        /* istanbul ignore next: graphic variation */ variant ===
          ButtonVariant.BOX && (
          <SvgIcon
            src={fullRightIcon}
            alt={svgAlt}
            className={cn(styles['button-icon'], styles['button-icon-arrow'])}
            width="22"
          />
        )
      }
    </>
  )

  const { to, isExternal, ...linkProps } = link

  // react-router v6 accepts relative links
  // That is, if you use "offers" as link, it will be relative to the current path
  // If you want a link to be absolute you must start it with a slash
  // As this behavior can be quite confusing, we decided to enforce absolute links
  // for internal links so that developers can't make mistakes/forget to add the slash
  const absoluteUrl = isExternal || to.startsWith('/') ? to : `/${to}`

  const callback: MouseEventHandler<HTMLAnchorElement> = e =>
    isDisabled ? e.preventDefault() : onClick?.(e)

  const disabled = isDisabled
    ? {
        'aria-disabled': true,
      }
    : {}

  const tooltipId = useId()
  const tooltipProps = hasTooltip ? { 'aria-describedby': tooltipId } : {}

  body = isExternal ? (
    <a
      className={classNames}
      href={absoluteUrl}
      onClick={callback}
      {...disabled}
      {...linkProps}
      {...tooltipProps}
    >
      {body}
    </a>
  ) : (
    /* istanbul ignore next: graphic variation */ <Link
      className={classNames}
      onClick={callback}
      to={absoluteUrl}
      {...disabled}
      {...tooltipProps}
      aria-label={linkProps['aria-label']}
    >
      {body}
    </Link>
  )

  if (hasTooltip) {
    body = (
      <Tooltip id={tooltipId} content={children}>
        {body}
      </Tooltip>
    )
  }

  return body
}

ButtonLink.variant = ButtonVariant

export default ButtonLink
