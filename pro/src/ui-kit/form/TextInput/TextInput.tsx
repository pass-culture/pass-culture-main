import { useField } from 'formik'
import React from 'react'

interface ITextInputProps {
  name: string
  className?: string
  disabled?: boolean
  label?: string
  placeholder?: string
}

const TextInput = ({
  name,
  className,
  disabled,
  label,
  placeholder,
}: ITextInputProps): JSX.Element => {
  const [field, meta] = useField({ name, disabled, className })

  return (
    <>
      <label>
        {label}
        <input {...field} placeholder={placeholder} />
      </label>
      {meta.touched && meta.error ? (
        <div className="error">{meta.error}</div>
      ) : null}
    </>
  )
}

export default TextInput
