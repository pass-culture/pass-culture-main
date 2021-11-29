import { useField } from 'formik'
import React from 'react'

interface ITextInputProps {
  name: string
  className?: string
  disabled?: boolean
  label?: string
  placeholder?: string
  type?: 'text' | 'number'
  maxLength?: number
}

const TextInput = ({
  name,
  type = 'text',
  className,
  disabled,
  label,
  placeholder,
  maxLength,
}: ITextInputProps): JSX.Element => {
  const [field, meta] = useField({ name, disabled })

  return (
    <>
      <label>
        {label}
        <input
          {...field}
          className={className}
          maxLength={maxLength}
          placeholder={placeholder}
          type={type}
        />
      </label>
      {meta.touched && meta.error ? (
        <div className="error">{meta.error}</div>
      ) : null}
    </>
  )
}

export default TextInput
