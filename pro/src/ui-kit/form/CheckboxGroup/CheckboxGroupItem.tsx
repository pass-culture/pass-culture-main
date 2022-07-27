import { useField } from 'formik'
import React from 'react'

import { BaseCheckbox } from '../shared'

interface ICheckboxProps {
  setGroupTouched(): void
  name: string
  label: string
  Icon?: React.FunctionComponent<React.SVGProps<SVGSVGElement>>
  hasError?: boolean
  disabled?: boolean
}

const CheckboxGroupItem = ({
  setGroupTouched,
  label,
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
      onChange={onChange}
      disabled={disabled}
    />
  )
}

export default CheckboxGroupItem
