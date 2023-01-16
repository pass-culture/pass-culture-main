import cn from 'classnames'
import React, { useState } from 'react'

import { uniqId } from 'utils/uniqId'

import styles from './BaseRadio.module.scss'

interface IBaseInputProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  label: string | JSX.Element
  hasError?: boolean
  className?: string
  withBorder?: boolean
}

const BaseInput = ({
  label,
  hasError,
  className,
  withBorder = false,
  ...props
}: IBaseInputProps): JSX.Element => {
  // TODO : https://stackoverflow.com/a/71681435 when upgrading React 18
  const [id] = useState(uniqId())

  return (
    <div
      className={cn(
        styles['base-radio'],
        {
          [styles['with-border']]: withBorder,
          [styles['with-border-primary']]: withBorder && props.checked,
        },
        className
      )}
    >
      <input
        type="radio"
        {...props}
        className={cn(styles['base-radio-input'], {
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
