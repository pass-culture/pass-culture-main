import cn from 'classnames'
import React, { useState, useId } from 'react'

import styles from './BaseRadio.module.scss'
import { BaseRadioVariant } from './types'

interface IBaseInputProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  label: string | JSX.Element
  hasError?: boolean
  className?: string
  withBorder?: boolean
  variant?: BaseRadioVariant
}

const BaseInput = ({
  label,
  hasError,
  className,
  withBorder = false,

  variant = /* istanbul ignore next: graphic variation */ BaseRadioVariant.PRIMARY,
  ...props
}: IBaseInputProps): JSX.Element => {
  // TODO : https://stackoverflow.com/a/71681435 when upgrading React 18
  const [id] = useState(useId())

  return (
    <div
      className={cn(
        styles['base-radio'],
        styles[`base-radio-${variant}`],
        {
          [styles[`with-border-${variant}`]]: withBorder,
          [styles[`with-border-${variant}-disabled`]]:
            withBorder && props.disabled,
          [styles[`with-border-${variant}-checked`]]:
            withBorder && props.checked && !props.disabled,
        },
        className
      )}
    >
      <input
        type="radio"
        {...props}
        className={cn(styles[`base-radio-${variant}-input`], {
          [styles['has-error']]: hasError,
        })}
        aria-invalid={hasError}
        id={id}
      />
      <label htmlFor={id} className={cn(styles['base-radio-label'])}>
        {label}
      </label>
    </div>
  )
}

export default BaseInput
