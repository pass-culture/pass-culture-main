/* istanbul ignore file : no need to test styled html tag  */

import cn from 'classnames'
import React, { useId } from 'react'

import IcoArrowRight from 'icons/ico-mini-arrow-right.svg'
import SpinnerIcon from 'icons/loader.svg'
import Tooltip from 'ui-kit/Tooltip'

import styles from './Button.module.scss'
import { ButtonVariant, IconPositionEnum, SharedButtonProps } from './types'

interface IButtonProps
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
  iconPosition = IconPositionEnum.LEFT,
  variant = ButtonVariant.PRIMARY,
  type = 'button',
  innerRef,
  hasTooltip,
  testId,
  isLoading = false,
  ...buttonAttrs
}: IButtonProps): JSX.Element => {
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
      {hasTooltip ? (
        <div className={styles['visually-hidden']}>
          {isLoading ? (
            <div className={styles['spinner-icon']}>
              <SpinnerIcon />
            </div>
          ) : (
            children
          )}
        </div>
      ) : variant === ButtonVariant.BOX ? (
        <div className={styles['button-arrow-content']}>
          {isLoading ? (
            <div className={styles['spinner-icon']}>
              <SpinnerIcon />
            </div>
          ) : (
            children
          )}
        </div>
      ) : isLoading ? (
        <div className={styles['spinner-icon']}>
          <SpinnerIcon />
        </div>
      ) : (
        children
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
