import cn from 'classnames'
import React, { MouseEventHandler } from 'react'
import { Link } from 'react-router-dom'

import styles from './Button.module.scss'
import { ButtonVariant, SharedButtonProps } from './types'

interface IButtonProps extends SharedButtonProps {
  to: string
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
  to,
  ...linkAttrs
}: IButtonProps): JSX.Element => {
  const isExternal = /^https?:\/\//i.test(to)

  const classNames = cn(
    styles['button'],
    styles[`button-${variant}`],
    { [styles[`button-disabled`]]: isDisabled },
    className
  )

  return isExternal ? (
    <a
      className={classNames}
      href={to}
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
      to={to}
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
