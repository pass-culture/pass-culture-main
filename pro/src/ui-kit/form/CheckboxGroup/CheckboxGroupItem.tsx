import { BaseCheckbox } from '../shared'
import React from 'react'
import { useField } from 'formik'

interface ICheckboxProps {
  setGroupTouched(): void
  name: string
  label: string
  Icon?: React.FunctionComponent<React.SVGProps<SVGSVGElement>>
  hasError?: boolean
}

const CheckboxGroupItem = ({
  setGroupTouched,
  label,
  name,
  hasError,
  Icon,
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
    />
  )
}

export default CheckboxGroupItem
