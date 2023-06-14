import { useField } from 'formik'
import React from 'react'

import { BaseCheckbox } from '../shared'

interface CheckboxGroupItemProps {
  setGroupTouched(): void
  name: string
  label: string
  description?: string
  icon?: string
  hasError?: boolean
  disabled?: boolean
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void
}

const CheckboxGroupItem = ({
  setGroupTouched,
  label,
  description,
  name,
  hasError,
  icon,
  disabled,
  onChange,
}: CheckboxGroupItemProps): JSX.Element => {
  const [field] = useField({ name, type: 'checkbox' })

  const onCustomChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setGroupTouched()
    field.onChange(event)
    if (onChange) {
      onChange(event)
    }
  }

  return (
    <BaseCheckbox
      {...field}
      icon={icon}
      hasError={hasError}
      label={label}
      description={description}
      onChange={onCustomChange}
      disabled={disabled}
    />
  )
}

export default CheckboxGroupItem
