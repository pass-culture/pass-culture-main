import { useField } from 'formik'
import React from 'react'

type Option = {
  value: string
  label: string
}

interface ISelectProps {
  name: string
  options: Option[]
  className?: string
  disabled?: boolean
  label?: string
}

const Select = ({
  name,
  options,
  className,
  disabled,
  label,
}: ISelectProps): JSX.Element => {
  const [field, meta] = useField({ name, type: 'select' })

  return (
    <>
      <label className={className}>
        {label}
        <select disabled={disabled} {...field}>
          {options.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
      {meta.touched && meta.error ? (
        <div className="error">{meta.error}</div>
      ) : null}
    </>
  )
}

export default Select
