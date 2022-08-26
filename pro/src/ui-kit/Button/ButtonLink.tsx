import cn from 'classnames'
import type { LocationDescriptor } from 'history'
import React, { MouseEventHandler, HTMLProps } from 'react'
import { Link } from 'react-router-dom'

import styles from './Button.module.scss'
import { ButtonVariant, SharedButtonProps } from './types'

type InternalLinkProps = Omit<HTMLProps<HTMLLinkElement>, 'onClick'> & {
  isExternal: false
  to: LocationDescriptor
}

type ExternalLinkProps = Omit<HTMLProps<HTMLAnchorElement>, 'onClick'> & {
  isExternal: true
  to: string
}
interface IButtonProps extends SharedButtonProps {
  link: InternalLinkProps | ExternalLinkProps
  children: React.ReactNode | React.ReactNode[]
  className?: string
  isDisabled?: boolean
  onClick?: MouseEventHandler<HTMLAnchorElement>
}

const linkIsExternal = (
  link: InternalLinkProps | ExternalLinkProps
): link is ExternalLinkProps => link.isExternal

const ButtonLink = ({
  className,
  children,
  Icon,
  isDisabled = false,
  onClick,
  variant = ButtonVariant.TERNARY,
  link,
}: IButtonProps): JSX.Element => {
  const classNames = cn(
    styles['button'],
    styles[`button-${variant}`],
    { [styles[`button-disabled`]]: isDisabled },
    className
  )

  if (linkIsExternal(link)) {
    const { to, ...linkProps } = link
    return (
      <a
        className={classNames}
        href={to}
        onClick={e => {
          isDisabled ? e.preventDefault() : onClick?.(e)
        }}
        {...(isDisabled ? { 'aria-disabled': true } : {})}
        {...linkProps}
      >
        {Icon && <Icon className={styles['button-icon']} />}
        {children}
      </a>
    )
  }

  return (
    <Link
      className={classNames}
      onClick={e => (isDisabled ? e.preventDefault() : onClick?.(e))}
      to={link.to}
      {...(isDisabled ? { 'aria-disabled': true } : {})}
    >
      {Icon && <Icon className={styles['button-icon']} />}
      {children}
    </Link>
  )
}

ButtonLink.variant = ButtonVariant

export default ButtonLink
