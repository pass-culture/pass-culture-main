import { useField } from 'formik'
import React from 'react'

interface TimePickerProps {
  name: string
  className?: string
  disabled?: boolean
  label?: string
}

const TimePicker = ({
  name,
  label,
  className,
  disabled,
}: TimePickerProps): JSX.Element => {
  const [field, meta] = useField({ name })

  return (
    <>
      <label>
        {label}
        <input
          {...field}
          className={className}
          disabled={disabled}
          type="time"
        />
      </label>
      {meta.touched && meta.error ? (
        <div className="error">{meta.error}</div>
      ) : null}
    </>
  )
}

export default TimePicker
