import cn from 'classnames'
import React, { ForwardedRef, forwardRef, useId } from 'react'

import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './BaseRadio.module.scss'

export enum RadioVariant {
  DEFAULT = 'DEFAULT',
  BOX = 'BOX',
}

export interface BaseRadioProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  label: string | JSX.Element
  hasError?: boolean
  className?: string
  variant?: RadioVariant
  ariaDescribedBy?: string
  childrenOnChecked?: JSX.Element
  icon?: string
  iconPosition?: 'center' | 'right'
  description?: string
}

export const BaseRadio = forwardRef(
  (
    {
      label,
      hasError,
      className,
      ariaDescribedBy,
      childrenOnChecked,
      variant = RadioVariant.DEFAULT,
      icon,
      iconPosition = 'right',
      description,
      ...props
    }: BaseRadioProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const id = useId()
    const descriptionId = useId()

    let describedBy = ariaDescribedBy ? ariaDescribedBy : ''
    describedBy += description ? ` ${descriptionId}` : ''

    const iconElement = icon ? (
      <SvgIcon src={icon} alt="" className={styles['base-radio-label-icon']} />
    ) : undefined

    return (
      <div
        className={cn(
          styles['radio'],
          icon ? styles[`icon-position-${iconPosition}`] : '',
          {
            [styles[`box-variant`]]: variant === RadioVariant.BOX,
            [styles[`has-children`]]: childrenOnChecked,
            [styles[`is-checked`]]: props.checked,
            [styles[`is-disabled`]]: props.disabled,
            [styles[`has-error`]]: hasError,
            [styles['has-icon']]: Boolean(icon),
          }
        )}
      >
        <div
          className={cn(
            styles['base-radio'],
            {
              [styles[`is-disabled`]]: props.disabled,
            },
            className
          )}
        >
          <input
            type="radio"
            {...props}
            className={cn(styles[`base-radio-input`], {
              [styles['has-error']]: hasError,
            })}
            aria-describedby={describedBy}
            aria-invalid={hasError}
            id={id}
            ref={ref}
          />
          <label htmlFor={id} className={styles['base-radio-label']}>
            <div className={styles['base-radio-label-left']}>
              {icon && iconPosition === 'center' && iconElement}
              <div className={styles['base-radio-label-text']}>{label}</div>
              {description && (
                <p
                  className={styles['base-radio-label-description']}
                  id={descriptionId}
                >
                  {description}
                </p>
              )}
            </div>
            {icon && iconPosition === 'right' && iconElement}
          </label>
        </div>
        {childrenOnChecked && props.checked && (
          <div className={styles['base-radio-children-on-checked']}>
            {childrenOnChecked}
          </div>
        )}
      </div>
    )
  }
)
BaseRadio.displayName = 'BaseRadio'
