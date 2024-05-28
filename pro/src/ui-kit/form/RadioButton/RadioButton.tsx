import cn from 'classnames'
import { useField } from 'formik'
import React, { useCallback } from 'react'

import { BaseRadio } from '../shared/BaseRadio/BaseRadio'

interface RadioButtonProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  name: string
  label: string | JSX.Element
  value: string
  withBorder?: boolean
  hasError?: boolean
  fullWidth?: boolean
}

export const RadioButton = ({
  disabled,
  name,
  label,
  value,
  withBorder,
  fullWidth,
  className,
  hasError,
  onChange,
}: RadioButtonProps): JSX.Element => {
  const [field] = useField({ name, value, type: 'radio' })

  const onCustomChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      field.onChange(e)
      if (onChange) {
        onChange(e)
      }
    },
    [field, onChange]
  )

  return (
    <BaseRadio
      {...field}
      disabled={disabled}
      id={name}
      label={label}
      value={value}
      className={cn(className)}
      checked={field.checked}
      hasError={hasError}
      withBorder={withBorder}
      fullWidth={fullWidth}
      onChange={(e) => onCustomChange(e)}
    />
  )
}
