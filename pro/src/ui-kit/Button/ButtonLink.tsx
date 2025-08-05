import cn from 'classnames'
import fullLinkIcon from 'icons/full-link.svg'
import React, { ForwardedRef, forwardRef, MouseEventHandler } from 'react'
import { Link } from 'react-router'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Button.module.scss'
import { ButtonVariant, IconPositionEnum, SharedButtonProps } from './types'

/**
 * Props for the ButtonLink component.
 *
 * @extends SharedButtonProps, React.HTMLProps<HTMLAnchorElement>
 */
export type LinkProps = {
  /**
   * If `true` the `to` prop should contain an absolute url.
   */
  isExternal?: boolean
  /**
   * Indicates if the link is a section link within the page.
   */
  isSectionLink?: boolean
  /**
   * The destination URL for the link.
   */
  to: string
  /**
   * If `true` the link will open in a new tab and the new tab icon will be displayed with an accessible label.
   */
  opensInNewTab?: boolean
  /**
   * ARIA label for the link, providing additional accessibility information.
   */
  'aria-label'?: string
}

/**
 * Props for the ButtonLink component that extends LinkProps and SharedButtonProps.
 */
export type ButtonLinkProps = LinkProps &
  SharedButtonProps &
  Omit<React.HTMLProps<HTMLAnchorElement>, 'title'>

/**
 * The ButtonLink component provides a button-like anchor link that supports internal and external navigation.
 * It integrates with React Router for internal links and supports a variety of styles and icons.
 *
 * @param {ButtonLinkProps} props - The props for the ButtonLink component.
 * @returns {JSX.Element} The rendered ButtonLink component.
 *
 * @example
 * <ButtonLink
 *   to="/about"
 *   variant={ButtonVariant.PRIMARY}
 *   icon={fullLinkIcon}
 *   iconAlt="Navigate to About Page"
 *   opensInNewTab={true}
 * >
 *   Learn More
 * </ButtonLink>
 *
 * @accessibility
 * - Provide meaningful ARIA labels for links without visible text to assist screen reader users.
 */
export const ButtonLink = forwardRef(
  (
    {
      className,
      children,
      icon,
      onClick,
      variant = ButtonVariant.TERNARY,
      iconPosition = IconPositionEnum.LEFT,
      iconAlt,
      onBlur,
      isExternal = false,
      isSectionLink = false,
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
      styles['button-link'],
      className
    )
    const svgIcon = opensInNewTab ? (
      <SvgIcon
        src={icon ?? fullLinkIcon}
        alt={iconAlt ?? 'Nouvelle fenêtre'}
        className={styles['button-icon']}
        width="22"
      />
    ) : icon ? (
      <SvgIcon
        src={icon}
        alt={iconAlt ?? ''}
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

    // Enforce absolute links for internal navigation to avoid mistakes.
    const absoluteUrl =
      isSectionLink || isExternal || to.startsWith('/') ? to : `/${to}`

    const callback: MouseEventHandler<HTMLAnchorElement> = (e) => onClick?.(e)

    body =
      isSectionLink || isExternal ? (
        <a
          className={classNames}
          href={absoluteUrl}
          onClick={callback}
          onBlur={(e) => onBlur?.(e)}
          rel="noopener noreferrer"
          {...props}
          target={props.target ?? (opensInNewTab ? '_blank' : '_self')}
          ref={forwadedRef}
        >
          {body}
        </a>
      ) : (
        <Link
          className={classNames}
          onClick={callback}
          onBlur={(e) => onBlur?.(e)}
          to={absoluteUrl}
          aria-label={props['aria-label']}
          target={props.target ?? (opensInNewTab ? '_blank' : '_self')}
          {...props}
          ref={forwadedRef}
        >
          {body}
        </Link>
      )

    return body
  }
)

// ButtonLink.variant = ButtonVariant
ButtonLink.displayName = 'ButtonLink'
