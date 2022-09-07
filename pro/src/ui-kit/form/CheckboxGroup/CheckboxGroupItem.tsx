import { useField } from 'formik'
import React from 'react'

import { BaseCheckbox } from '../shared'

interface ICheckboxProps {
  setGroupTouched(): void
  name: string
  label: string
  description?: string
  Icon?: React.FunctionComponent<React.SVGProps<SVGSVGElement>>
  hasError?: boolean
  disabled?: boolean
}

const CheckboxGroupItem = ({
  setGroupTouched,
  label,
  description,
  name,
  hasError,
  Icon,
  disabled,
}: ICheckboxProps): JSX.Element => {
  const [field] = useField({ name, type: 'checkbox' })

  const onChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setGroupTouched()
    field.onChange(event)
  }

  return (
    <BaseCheckbox
      {...field}
      Icon={Icon}
      hasError={hasError}
      label={label}
      description={description}
      onChange={onChange}
      disabled={disabled}
    />
  )
}

export default CheckboxGroupItem
