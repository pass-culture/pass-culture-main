import cn from 'classnames'
import React from 'react'

import styles from './BaseRadio.module.scss'

interface IBaseInputProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  label: string
  hasError?: boolean
  className?: string
}

const BaseInput = ({
  label,
  hasError,
  className,
  ...props
}: IBaseInputProps): JSX.Element => (
  <label className={cn(styles['base-radio'], className)}>
    <input
      type="radio"
      {...props}
      className={cn(styles['base-radio-input'], {
        [styles['has-error']]: hasError,
      })}
    />
    <span
      className={cn(styles['base-radio-label'], {
        [styles['base-radio-label-checked']]: props.checked,
      })}
    >
      {label}
    </span>
  </label>
)

export default BaseInput
