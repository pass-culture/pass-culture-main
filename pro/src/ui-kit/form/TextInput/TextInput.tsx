import { useField } from 'formik'
import React from 'react'

interface ITextInputProps {
  name: string;
  className?: string;
  disabled?: boolean;
  label?: string;
}

const TextInput = ({ 
  name,
  className,
  disabled,
  label,
}: ITextInputProps): JSX.Element => {
  const [field, meta] = useField({ name, disabled, className })

  return (
    <>
      <label>
        {label}
        <input {...field} />
      </label>
      {meta.touched && meta.error ? (
        <div className="error">
          {meta.error}
        </div>
      ) : null}
    </>
  )
}

export default TextInput
