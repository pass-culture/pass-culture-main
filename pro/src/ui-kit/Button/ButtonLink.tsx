import cn from 'classnames'
import React, { MouseEventHandler, useRef } from 'react'
import { Link } from 'react-router-dom'

import styles from './Button.module.scss'
import { ButtonVariant, IconPositionEnum, SharedButtonProps } from './types'
import useTooltipMargin from './useTooltipMargin'

export type LinkProps = {
  isExternal: boolean
  to: string
  rel?: string
  target?: string
  'aria-label'?: string
}
interface IButtonProps extends SharedButtonProps {
  link: LinkProps
  children?: React.ReactNode | React.ReactNode[]
  className?: string
  isDisabled?: boolean
  onClick?: MouseEventHandler<HTMLAnchorElement>
  hasTooltip?: boolean
}

const ButtonLink = ({
  className,
  children,
  Icon,
  isDisabled = false,
  onClick,
  variant = ButtonVariant.TERNARY,
  link,
  iconPosition = IconPositionEnum.LEFT,
  hasTooltip = false,
}: IButtonProps): JSX.Element => {
  const tooltipRef = useRef<HTMLDivElement>(null)
  const tooltipMargin = useTooltipMargin(tooltipRef, children)

  const classNames = cn(
    styles['button'],
    styles[`button-${variant}`],
    { [styles[`button-disabled`]]: isDisabled },
    className
  )
  const renderBody = () => (
    <>
      {Icon && iconPosition !== IconPositionEnum.RIGHT && (
        <Icon className={styles['button-icon']} />
      )}
      {hasTooltip ? (
        <div
          className={styles.tooltip}
          ref={tooltipRef}
          style={{ marginTop: tooltipMargin }}
        >
          {children}
        </div>
      ) : (
        children
      )}
      {Icon && iconPosition === IconPositionEnum.RIGHT && (
        <Icon className={styles['button-icon']} />
      )}
    </>
  )
  const { to, isExternal, ...linkProps } = link
  const callback: MouseEventHandler<HTMLAnchorElement> = e =>
    isDisabled ? e.preventDefault() : onClick?.(e)

  return isExternal ? (
    <a
      className={classNames}
      href={to}
      onClick={callback}
      {...(isDisabled
        ? {
            'aria-disabled': true,
          }
        : {})}
      {...linkProps}
    >
      {renderBody()}
    </a>
  ) : (
    /* istanbul ignore next : no need to test react navigation */ <Link
      className={classNames}
      onClick={callback}
      to={to}
      {...(isDisabled
        ? {
            'aria-disabled': true,
          }
        : {})}
    >
      {renderBody()}
    </Link>
  )
}

ButtonLink.variant = ButtonVariant

export default ButtonLink
