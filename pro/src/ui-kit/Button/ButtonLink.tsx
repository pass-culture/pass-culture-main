import cn from 'classnames'
import type { LocationDescriptor } from 'history'
import React, { MouseEventHandler, HTMLProps } from 'react'
import { Link } from 'react-router-dom'

import styles from './Button.module.scss'
import { ButtonVariant, IconPositionEnum, SharedButtonProps } from './types'

export type InternalLinkProps = Omit<HTMLProps<HTMLLinkElement>, 'onClick'> & {
  isExternal: false
  to: LocationDescriptor
}

export type ExternalLinkProps = Omit<
  HTMLProps<HTMLAnchorElement>,
  'onClick'
> & {
  isExternal: true
  to: string
}
interface IButtonProps extends SharedButtonProps {
  link: InternalLinkProps | ExternalLinkProps
  children?: React.ReactNode | React.ReactNode[]
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
  iconPosition = IconPositionEnum.LEFT,
}: IButtonProps): JSX.Element => {
  const classNames = cn(
    styles['button'],
    styles[`button-${variant}`],
    { [styles[`button-disabled`]]: isDisabled },
    className
  )

  if (linkIsExternal(link)) {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { to, isExternal, ...linkProps } = link
    return (
      <a
        className={classNames}
        href={to}
        onClick={e => {
          /* istanbul ignore next: Graphic variations */
          isDisabled ? e.preventDefault() : onClick?.(e)
        }}
        {...(isDisabled
          ? /* istanbul ignore next: Graphic variations */ {
              'aria-disabled': true,
            }
          : /* istanbul ignore next: Graphic variations */ {})}
        {...linkProps}
      >
        {
          /* istanbul ignore next: Graphic variations */
          Icon && iconPosition === IconPositionEnum.LEFT && (
            <Icon
              className={cn(styles['button-icon'], styles['button-icon-left'])}
            />
          )
        }
        {children}
        {
          /* istanbul ignore next: Graphic variations */
          Icon && iconPosition === IconPositionEnum.RIGHT && (
            <Icon
              className={cn(styles['button-icon'], styles['button-icon-right'])}
            />
          )
        }
      </a>
    )
  }

  return (
    <Link
      className={classNames}
      onClick={e =>
        /* istanbul ignore next: Graphic variations */
        isDisabled ? e.preventDefault() : onClick?.(e)
      }
      to={link.to}
      {...(isDisabled ? { 'aria-disabled': true } : {})}
    >
      {
        /* istanbul ignore next: Graphic variations */
        Icon && iconPosition === IconPositionEnum.LEFT && (
          <Icon
            className={cn(styles['button-icon'], styles['button-icon-left'])}
          />
        )
      }
      {children}
      {
        /* istanbul ignore next: Graphic variations */
        Icon && iconPosition === IconPositionEnum.RIGHT && (
          <Icon
            className={cn(styles['button-icon'], styles['button-icon-right'])}
          />
        )
      }
    </Link>
  )
}

ButtonLink.variant = ButtonVariant

export default ButtonLink
