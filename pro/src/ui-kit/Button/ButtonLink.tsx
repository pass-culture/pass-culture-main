import cn from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'

import styles from './Button.module.scss'
import { SharedButtonProps, ButtonVariant } from './types'

interface IButtonProps extends SharedButtonProps {
  to: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
  isDisabled?: boolean
}

const ButtonLink = ({
  className,
  children,
  Icon,
  isDisabled = false,
  variant = ButtonVariant.TERNARY,
  to,
  ...linkAttrs
}: IButtonProps): JSX.Element => {
  const isExternal = /^https?:\/\//i.test(to)

  const classNames = cn(
    styles['button'],
    styles[`button-${variant}`],
    isDisabled ? styles[`button-disabled`] : null,
    className
  )

  return isExternal ? (
    <a
      className={classNames}
      href={to}
      {...linkAttrs}
      {...(isDisabled ? 'aria-disabled' : undefined)}
    >
      {Icon && <Icon className={styles['button-icon']} />}
      {children}
    </a>
  ) : (
    <Link className={classNames} to={to} {...linkAttrs}>
      {Icon && <Icon className={styles['button-icon']} />}
      {children}
    </Link>
  )
}

ButtonLink.variant = ButtonVariant

export default ButtonLink
