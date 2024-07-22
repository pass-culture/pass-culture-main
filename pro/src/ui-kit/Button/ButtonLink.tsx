import cn from 'classnames'
import React, { ForwardedRef, forwardRef, MouseEventHandler } from 'react'
import { Link } from 'react-router-dom'

import fullLinkIcon from 'icons/full-link.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Button.module.scss'
import { ButtonVariant, IconPositionEnum, SharedButtonProps } from './types'

export type LinkProps = {
  isDisabled?: boolean
  svgAlt?: string
  isExternal?: boolean
  to: string
  opensInNewTab?: boolean
  'aria-label'?: string
  type?: string
  download?: boolean
}

type ButtonLinkProps = LinkProps &
  SharedButtonProps &
  React.HTMLProps<HTMLAnchorElement>

export const ButtonLink = forwardRef(
  (
    {
      className,
      children,
      icon,
      isDisabled = false,
      onClick,
      variant = ButtonVariant.TERNARY,
      iconPosition = IconPositionEnum.LEFT,
      svgAlt,
      onBlur,
      isExternal = false,
      opensInNewTab,
      to,
      ...props
    }: ButtonLinkProps,
    forwadedRef: ForwardedRef<HTMLAnchorElement>
  ): JSX.Element => {
    const classNames = cn(
      styles['button'],
      styles[`button-${variant}`],
      styles[`button-${iconPosition}`],
      { [styles['button-disabled'] ?? '']: isDisabled },
      styles['button-link'],
      className
    )
    const svgIcon = opensInNewTab ? (
      <SvgIcon
        src={icon ?? fullLinkIcon}
        alt={svgAlt ?? 'Nouvelle fenêtre'}
        className={styles['button-icon']}
        width="22"
      />
    ) : icon ? (
      <SvgIcon
        src={icon}
        alt={svgAlt ?? ''}
        className={styles['button-icon']}
        width="22"
      />
    ) : null

    let body = (
      <>
        {iconPosition !== IconPositionEnum.RIGHT && svgIcon}
        {variant === ButtonVariant.BOX ? (
          <div className={styles['button-arrow-content']}>{children}</div>
        ) : (
          <>{children}</>
        )}
        {iconPosition === IconPositionEnum.RIGHT && svgIcon}
      </>
    )

    // react-router v6 accepts relative links
    // That is, if you use "offers" as link, it will be relative to the current path
    // If you want a link to be absolute you must start it with a slash
    // As this behavior can be quite confusing, we decided to enforce absolute links
    // for internal links so that developers can't make mistakes/forget to add the slash
    const absoluteUrl = isExternal || to.startsWith('/') ? to : `/${to}`

    const callback: MouseEventHandler<HTMLAnchorElement> = (e) =>
      isDisabled ? e.preventDefault() : onClick?.(e)

    const disabled = isDisabled ? (
      <span className="visually-hidden">Action non disponible</span>
    ) : (
      <></>
    )

    body = isExternal ? (
      <a
        className={classNames}
        href={absoluteUrl}
        onClick={callback}
        onBlur={(e) => onBlur?.(e)}
        rel="noopener noreferrer"
        {...props}
        target={opensInNewTab ? '_blank' : '_self'}
        ref={forwadedRef}
      >
        {body}
        {disabled}
      </a>
    ) : (
      <Link
        className={classNames}
        onClick={callback}
        onBlur={(e) => onBlur?.(e)}
        to={absoluteUrl}
        aria-label={props['aria-label']}
        target={opensInNewTab ? '_blank' : '_self'}
        {...props}
        ref={forwadedRef}
      >
        {body}
        {disabled}
      </Link>
    )

    return body
  }
)

// ButtonLink.variant = ButtonVariant
ButtonLink.displayName = 'ButtonLink'
