import cn from 'classnames'
import React, { useId } from 'react'

import styles from './BaseRadio.module.scss'

interface BaseRadioProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  label: string | JSX.Element
  hasError?: boolean
  className?: string
  withBorder?: boolean
  ariaDescribedBy?: string
  childrenOnChecked?: JSX.Element
}

export const BaseRadio = ({
  label,
  hasError,
  className,
  withBorder = false,
  ariaDescribedBy,
  childrenOnChecked,
  ...props
}: BaseRadioProps): JSX.Element => {
  const id = useId()
  const childrenContainerId = useId()

  return (
    <div
      className={cn(styles['radio'], {
        [styles[`with-border`]]: withBorder,
        [styles[`has-children`]]: childrenOnChecked,
        [styles[`is-checked`]]: props.checked,
        [styles[`is-disabled`]]: props.disabled,
        [styles[`has-error`]]: hasError,
      })}
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
          {...(ariaDescribedBy ? { 'aria-describedby': ariaDescribedBy } : {})}
          aria-invalid={hasError}
          id={id}
        />
        <label htmlFor={id} className={styles['base-radio-label']}>
          {label}
        </label>
      </div>
      <div id={childrenContainerId}>
        {childrenOnChecked && props.checked && (
          <div className={styles['base-radio-children-on-checked']}>
            {childrenOnChecked}
          </div>
        )}
      </div>
    </div>
  )
}
