import { useField } from 'formik'
import React from 'react'

type Option = {
    value: string, label: string
}

interface ISelectProps {
  name: string;
  options: Option[];
  className?: string;
  disabled?: boolean;
  label?: string;
}

const Select= ({
  name,
  options,
  className,
  disabled,
  label,
}: ISelectProps): JSX.Element => {
  const [field, meta] = useField({ name })

  return (
    <>
      <label>
        {label}
        <select
          {...field}
          className={className}
          disabled={disabled}
        >
          {options.map(option => (
            <option
              key={option.value}
              value={option.value}
            >
              {option.label}
            </option>
          ))}
        </select>
      </label>
      {
        meta.touched && meta.error ? (
          <div className="error">
            {meta.error}
          </div>
        ) : null
      }
    </>
  )
}

export default Select
