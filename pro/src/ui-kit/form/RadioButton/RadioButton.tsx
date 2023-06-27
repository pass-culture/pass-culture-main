import cn from 'classnames'
import { useField } from 'formik'
import React, { useCallback } from 'react'

import { BaseRadio } from '../shared'
import { BaseRadioVariant } from '../shared/BaseRadio/types'

interface RadioButtonProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  name: string
  label: string | JSX.Element
  value: string
  withBorder?: boolean
  hasError?: boolean
  variant?: BaseRadioVariant
}

const RadioButton = ({
  disabled,
  name,
  label,
  value,
  withBorder,
  className,
  hasError,
  variant = BaseRadioVariant.PRIMARY,
  onChange,
}: RadioButtonProps): JSX.Element => {
  const [field] = useField({ name, value, type: 'radio' })

  const onCustomChange = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
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
      variant={variant}
      onChange={e => onCustomChange(e)}
    />
  )
}

export default RadioButton
