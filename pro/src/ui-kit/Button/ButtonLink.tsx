import cn from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'

import styles from './Button.module.scss'
import { SharedButtonProps, ButtonVariant } from './types'

interface IButtonProps extends SharedButtonProps {
  to: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const ButtonLink = ({
  className,
  children,
  Icon,
  variant = ButtonVariant.TERNARY,
  to,
  ...linkAttrs
}: IButtonProps): JSX.Element => {
  const isExternal = /^https?:\/\//i.test(to)

  const classNames = cn(
    styles['button'],
    styles[`button-${variant}`],
    className
  )

  return isExternal ? (
    <a className={classNames} href={to} {...linkAttrs}>
      {Icon && <Icon />}
      {children}
    </a>
  ) : (
    <Link className={classNames} to={to} {...linkAttrs}>
      {Icon && <Icon />}
      {children}
    </Link>
  )
}

ButtonLink.variant = ButtonVariant

export default ButtonLink
