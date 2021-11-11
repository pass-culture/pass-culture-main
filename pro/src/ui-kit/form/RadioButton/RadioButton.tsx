import { useField } from 'formik'
import React from 'react'

interface IRadioButtonProps {
  name: string;
  label: string;
  value: string;
  className?: string;
}

const RadioButton = ({
  name,
  label,
  value,
  className,
}: IRadioButtonProps): JSX.Element => {
  const [field, meta] = useField({ name })

  return (
    <>
      <label>
        <input
          {...field}
          className={className}
          type="radio"
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

export default RadioButton
