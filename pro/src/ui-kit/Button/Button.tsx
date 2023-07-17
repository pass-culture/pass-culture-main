/* istanbul ignore file : no need to test styled html tag  */

import cn from 'classnames'
import React, { useId } from 'react'

import fullRightIcon from 'icons/full-right.svg'
import strokePassIcon from 'icons/stroke-pass.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import Tooltip from 'ui-kit/Tooltip'

import styles from './Button.module.scss'
import { ButtonVariant, IconPositionEnum, SharedButtonProps } from './types'

export interface ButtonProps
  extends SharedButtonProps,
    React.HTMLProps<HTMLButtonElement> {
  type?: 'button' | 'submit'
  innerRef?: React.RefObject<HTMLButtonElement>
  className?: string
  hasTooltip?: boolean
  isLoading?: boolean
}

const Button = ({
  className,
  children,
  icon,
  iconPosition = IconPositionEnum.LEFT,
  variant = ButtonVariant.PRIMARY,
  type = 'button',
  innerRef,
  hasTooltip,
  testId,
  isLoading = false,
  ...buttonAttrs
}: ButtonProps): JSX.Element => {
  const tooltipId = useId()

  const button = (
    <button
      className={cn(
        styles['button'],
        styles[`button-${variant}`],
        styles[`button-${iconPosition}`],
        { [styles['loading-spinner']]: isLoading },
        className
      )}
      ref={innerRef}
      type={type}
      data-testid={testId}
      {...(hasTooltip ? { 'aria-describedby': tooltipId } : {})}
      {...buttonAttrs}
    >
      {icon && iconPosition !== IconPositionEnum.RIGHT && (
        <SvgIcon
          src={icon}
          alt=""
          className={cn(styles['button-icon'], {
            [styles['has-tooltip']]: hasTooltip,
          })}
          width="20"
        />
      )}
      {hasTooltip ? (
        <div className={styles['visually-hidden']}>
          {isLoading ? (
            <div className={styles['spinner-icon']} data-testid="spinner">
              <SvgIcon src={strokePassIcon} alt="" />
            </div>
          ) : (
            children
          )}
        </div>
      ) : variant === ButtonVariant.BOX ? (
        <div className={styles['button-arrow-content']}>
          {isLoading ? (
            <div className={styles['spinner-icon']} data-testid="spinner">
              <SvgIcon src={strokePassIcon} alt="" />
            </div>
          ) : (
            children
          )}
        </div>
      ) : isLoading ? (
        <div className={styles['spinner-icon']} data-testid="spinner">
          <SvgIcon src={strokePassIcon} alt="" />
        </div>
      ) : (
        children
      )}
      {icon && iconPosition === IconPositionEnum.RIGHT && (
        <SvgIcon
          src={icon}
          alt=""
          className={styles['button-icon']}
          width="20"
        />
      )}
      {variant === ButtonVariant.BOX && (
        <SvgIcon
          src={fullRightIcon}
          alt=""
          className={cn(styles['button-icon'], styles['button-icon-arrow'])}
          width="20"
        />
      )}
    </button>
  )

  if (hasTooltip && !buttonAttrs?.disabled) {
    return (
      <Tooltip id={tooltipId} content={children}>
        {button}
      </Tooltip>
    )
  }

  return button
}

export default Button
