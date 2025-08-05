import cn from 'classnames'
import strokeSearchIcon from 'icons/stroke-search.svg'
import React, { ForwardedRef, forwardRef } from 'react'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './BaseInput.module.scss'

export interface BaseInputProps
  extends Partial<
    Omit<React.InputHTMLAttributes<HTMLInputElement>, 'placeholder'>
  > {
  className?: string
  hasError?: boolean
  filterVariant?: boolean
  leftIcon?: string
  rightIcon?: string
  rightButton?: () => JSX.Element
  id?: string
}

export const BaseInput = forwardRef(
  (
    {
      className,
      hasError,
      filterVariant,
      name,
      leftIcon,
      rightIcon,
      rightButton,
      id,
      ...props
    }: BaseInputProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    if (props.type === 'search') {
      rightIcon = undefined
      leftIcon = strokeSearchIcon
    }

    if (rightIcon || leftIcon || rightButton) {
      const hasRightIcon = !leftIcon && !!rightIcon
      const hasButton = !!rightButton

      return (
        <div className={styles['base-input-wrapper']}>
          <input
            {...props}
            aria-invalid={hasError}
            {...(hasError
              ? { 'aria-describedby': `error-details-${name}` }
              : {})}
            placeholder={props.type === 'search' ? 'Rechercher' : undefined}
            className={cn(
              styles['base-input'],
              {
                [styles['base-input-with-right-icon']]: hasRightIcon,
                [styles['base-input-with-left-icon']]: Boolean(leftIcon),
                [styles['has-error']]: hasError,
                [styles['filter-variant']]: filterVariant,
              },
              className
            )}
            id={id ?? name}
            name={name}
            ref={ref}
          />
          <span
            className={cn({
              [styles['base-input-right-icon']]: hasRightIcon,
              [styles['base-input-left-icon']]: Boolean(leftIcon),
              [styles['base-input-right-button']]: hasButton,
              [styles['filter-variant']]: filterVariant,
            })}
          >
            {leftIcon && <SvgIcon src={leftIcon} alt="" />}
            {hasRightIcon && rightIcon && <SvgIcon src={rightIcon} alt="" />}
            {hasButton && rightButton()}
          </span>
        </div>
      )
    } else {
      return (
        <input
          {...props}
          aria-invalid={hasError}
          {...(hasError ? { 'aria-describedby': `error-${name}` } : {})}
          className={cn(
            styles['base-input'],
            {
              [styles['has-error']]: hasError,
              [styles['filter-variant']]: filterVariant,
            },
            className
          )}
          id={id ?? name}
          name={name}
          ref={ref}
        />
      )
    }
  }
)
BaseInput.displayName = 'BaseInput'
