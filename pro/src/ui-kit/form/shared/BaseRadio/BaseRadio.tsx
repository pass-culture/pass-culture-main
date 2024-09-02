import cn from 'classnames'
import React, { useId } from 'react'

import styles from './BaseRadio.module.scss'

interface BaseRadioProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  label: string | JSX.Element
  hasError?: boolean
  className?: string
  withBorder?: boolean
  fullWidth?: boolean
  ariaDescribedBy?: string
}

export const BaseRadio = ({
  label,
  hasError,
  className,
  withBorder = false,
  fullWidth = false,
  ariaDescribedBy,
  ...props
}: BaseRadioProps): JSX.Element => {
  const id = useId()

  return (
    <div
      className={cn(
        styles['base-radio'],
        {
          [styles[`with-border`]]: withBorder,
          [styles[`is-disabled`]]: props.disabled,
          [styles[`full-width`]]: fullWidth,
          [styles[`with-border-checked`]]:
            withBorder && props.checked && !props.disabled,
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
      <label htmlFor={id} className={cn(styles['base-radio-label'])}>
        {label}
      </label>
    </div>
  )
}
