import { useField } from 'formik'
import React from 'react'

interface ICheckboxProps {
  name: string;
  value: string;
  label: string;
  className?: string;
}

const Checkbox = ({
  name,
  value,
  label,
  className,
}: ICheckboxProps): JSX.Element => {
  const [field, meta] = useField({ name })

  return (
    <>
      <label>
        <input
          {...field}
          className={className}
          type="checkbox"
          value={value}
        />
        {label}
      </label>
      {
        meta.touched && meta.error ? (
          <div className="error">
            {meta.error}
          </div>
        )
          : null
      }
    </>
  )
}

export default Checkbox