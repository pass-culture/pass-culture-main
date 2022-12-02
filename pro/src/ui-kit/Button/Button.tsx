/* istanbul ignore file : no need to test styled html tag  */

import cn from 'classnames'
import React, { useRef } from 'react'

import { ReactComponent as IcoArrowRight } from 'icons/ico-mini-arrow-right.svg'

import styles from './Button.module.scss'
import { ButtonVariant, IconPositionEnum, SharedButtonProps } from './types'
import useTooltipMargin from './useTooltipMargin'

interface IButtonProps
  extends SharedButtonProps,
    React.HTMLProps<HTMLButtonElement> {
  type?: 'button' | 'submit'
  innerRef?: React.RefObject<HTMLButtonElement>
  className?: string
  hasTooltip?: boolean
}

const Button = ({
  className,
  children,
  Icon,
  iconPosition = IconPositionEnum.LEFT,
  variant = ButtonVariant.PRIMARY,
  type = 'button',
  innerRef,
  hasTooltip,
  ...buttonAttrs
}: IButtonProps): JSX.Element => {
  const tooltipRef = useRef<HTMLDivElement>(null)
  const tooltipMargin = useTooltipMargin(tooltipRef, children)

  return (
    <button
      className={cn(
        styles['button'],
        styles[`button-${variant}`],
        styles[`button-${iconPosition}`],
        className
      )}
      ref={innerRef}
      type={type}
      {...buttonAttrs}
    >
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
      ) : variant === ButtonVariant.BOX ? (
        <div className={styles['button-arrow-content']}>{children}</div>
      ) : (
        children
      )}
      {Icon && iconPosition === IconPositionEnum.RIGHT && (
        <Icon className={styles['button-icon']} />
      )}
      {variant === ButtonVariant.BOX && (
        <IcoArrowRight
          className={cn(styles['button-icon'], styles['button-icon-arrow'])}
        />
      )}
    </button>
  )
}

export default Button
