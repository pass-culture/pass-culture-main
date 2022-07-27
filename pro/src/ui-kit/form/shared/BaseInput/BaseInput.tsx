import cn from 'classnames'
import React, { ForwardedRef, forwardRef } from 'react'

import styles from './BaseInput.module.scss'

interface IBaseInputProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  className?: string
  hasError?: boolean
  rightIcon?: () => JSX.Element
  rightButton?: () => JSX.Element
}

const BaseInput = forwardRef(
  (
    {
      className,
      hasError,
      name,
      rightIcon,
      rightButton,
      ...props
    }: IBaseInputProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    if (rightIcon || rightButton) {
      const hasIcon = !!rightIcon
      const hasButton = !!rightButton

      return (
        <div className={styles['base-input-wrapper']}>
          <input
            {...props}
            aria-invalid={hasError}
            className={cn(
              styles['base-input'],
              styles['base-input-with-right-icon'],
              {
                [styles['has-error']]: hasError,
              },
              className
            )}
            id={name}
            name={name}
            ref={ref}
          />
          <span
            className={cn({
              [styles['base-input-right-icon']]: hasIcon,
              [styles['base-input-right-button']]: hasButton,
            })}
          >
            {hasIcon ? rightIcon() : hasButton && rightButton()}
          </span>
        </div>
      )
    } else {
      return (
        <input
          {...props}
          aria-invalid={hasError}
          className={cn(
            styles['base-input'],
            {
              [styles['has-error']]: hasError,
            },
            className
          )}
          id={name}
          name={name}
          ref={ref}
        />
      )
    }
  }
)
BaseInput.displayName = 'BaseInput'
export default BaseInput
