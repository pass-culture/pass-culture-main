import { useField } from 'formik'
import React from 'react'

interface IRadioButtonProps {
  name: string
  label: string
  value: string
  className?: string
  checked?: boolean
}

const RadioButton = ({
  name,
  label,
  value,
  className,
}: IRadioButtonProps): JSX.Element => {
  const [field, meta] = useField({ name, value, type: 'radio' })

  return (
    <div className={className}>
      <label>
        <input {...field} type="radio" value={value} />
        {label}
      </label>
      {meta.touched && meta.error ? (
        <div className="error">{meta.error}</div>
      ) : null}
    </div>
  )
}

export default RadioButton
