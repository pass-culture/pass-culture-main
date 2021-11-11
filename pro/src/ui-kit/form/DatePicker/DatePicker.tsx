import { useField } from 'formik'
import React from 'react'

interface DatePickerProps {
    name: string;
    className?: string;
    disabled?: boolean;
    label?: string;
}

const DatePicker = ({
  name,
  className,
  disabled,
  label,
}: DatePickerProps): JSX.Element => {
  const [field, meta] = useField({ name })

  return (
    <>
      <label>
        {label}
        <input
          {...field}
          className={className}
          disabled={disabled}
          type="date"
        />
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

export default DatePicker
