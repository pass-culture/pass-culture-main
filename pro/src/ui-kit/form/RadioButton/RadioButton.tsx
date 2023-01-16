import cn from 'classnames'
import { useField } from 'formik'
import React from 'react'

import { BaseRadio } from '../shared'

interface IRadioButtonProps {
  disabled?: boolean
  name: string
  label: string | JSX.Element
  value: string
  className?: string
  checked?: boolean
  withBorder?: boolean
  hasError?: boolean
}

const RadioButton = ({
  disabled,
  name,
  label,
  value,
  withBorder,
  className,
  hasError,
}: IRadioButtonProps): JSX.Element => {
  const [field] = useField({ name, value, type: 'radio' })

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
    />
  )
}

export default RadioButton
