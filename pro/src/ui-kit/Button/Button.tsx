/* istanbul ignore file : no need to test styled html tag  */

import cn from 'classnames'
import React from 'react'

import fullRightIcon from 'icons/full-right.svg'
import strokePassIcon from 'icons/stroke-pass.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import Tooltip from 'ui-kit/Tooltip'
import { useTooltipProps } from 'ui-kit/Tooltip/useTooltipProps'

import styles from './Button.module.scss'
import { ButtonVariant, IconPositionEnum, SharedButtonProps } from './types'

export interface ButtonProps
  extends SharedButtonProps,
    React.HTMLProps<HTMLButtonElement> {
  type?: 'button' | 'submit'
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
  hasTooltip,
  testId,
  isLoading = false,
  ...buttonAttrs
}: ButtonProps): JSX.Element => {
  const { isTooltipHidden, ...tooltipProps } = useTooltipProps(buttonAttrs)
  const loadingDiv = (
    <div className={styles['spinner-icon']} data-testid="spinner">
      <SvgIcon src={strokePassIcon} alt="" />
    </div>
  )
  const content = (
    <>
      {icon && !isLoading && iconPosition !== IconPositionEnum.RIGHT && (
        <SvgIcon
          src={icon}
          alt=""
          className={cn(styles['button-icon'], {
            [styles['has-tooltip']]: hasTooltip,
          })}
          width="20"
        />
      )}
      {variant === ButtonVariant.BOX ? (
        <div
          className={cn({
            [styles['button-arrow-content']]: variant === ButtonVariant.BOX,
          })}
        ></div>
      ) : (
        <>
          {isLoading && loadingDiv}
          {!isLoading && !hasTooltip && children}
        </>
      )}

      {icon && !isLoading && iconPosition === IconPositionEnum.RIGHT && (
        <SvgIcon
          src={icon}
          alt=""
          className={styles['button-icon']}
          width="20"
        />
      )}
      {!isLoading && variant === ButtonVariant.BOX && (
        <SvgIcon
          src={fullRightIcon}
          alt=""
          className={cn(styles['button-icon'], styles['button-icon-arrow'])}
          width="20"
        />
      )}
    </>
  )

  return (
    <button
      className={cn(
        styles['button'],
        styles[`button-${variant}`],
        styles[`button-${iconPosition}`],
        { [styles['loading-spinner']]: isLoading },
        className
      )}
      type={type}
      data-testid={testId}
      {...buttonAttrs}
      {...(hasTooltip && tooltipProps)}
    >
      {hasTooltip ? (
        <Tooltip content={children} visuallyHidden={isTooltipHidden}>
          {content}
        </Tooltip>
      ) : (
        content
      )}
    </button>
  )
}

export default Button
