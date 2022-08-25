import cn from 'classnames'
import type { LocationDescriptor } from 'history'
import React, { MouseEventHandler } from 'react'
import { Link } from 'react-router-dom'

import styles from './Button.module.scss'
import { ButtonVariant, SharedButtonProps } from './types'

type InternalLinkProps = {
  isExternal: false
  to: LocationDescriptor
}

type ExternalLinkProps = {
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

const ButtonLink = ({
  className,
  children,
  Icon,
  isDisabled = false,
  onClick,
  variant = ButtonVariant.TERNARY,
  link,
  ...linkAttrs
}: IButtonProps): JSX.Element => {
  const classNames = cn(
    styles['button'],
    styles[`button-${variant}`],
    { [styles[`button-disabled`]]: isDisabled },
    className
  )

  return link.isExternal ? (
    <a
      className={classNames}
      href={link.to}
      onClick={e => {
        isDisabled ? e.preventDefault() : onClick?.(e)
      }}
      {...linkAttrs}
      {...(isDisabled ? { 'aria-disabled': true } : {})}
    >
      {Icon && <Icon className={styles['button-icon']} />}
      {children}
    </a>
  ) : (
    <Link
      className={classNames}
      onClick={e => (isDisabled ? e.preventDefault() : onClick?.(e))}
      to={link.to}
      {...linkAttrs}
      {...(isDisabled ? { 'aria-disabled': true } : {})}
    >
      {Icon && <Icon className={styles['button-icon']} />}
      {children}
    </Link>
  )
}

ButtonLink.variant = ButtonVariant

export default ButtonLink
