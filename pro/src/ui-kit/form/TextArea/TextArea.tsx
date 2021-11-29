import { useField } from 'formik'
import React from 'react'

interface ITextAreaProps {
  name: string
  className?: string
  disabled?: boolean
  placeholder?: string
  label?: string
  maxLength?: number
}

const TextArea = ({
  name,
  className,
  disabled,
  placeholder,
  label,
  maxLength,
}: ITextAreaProps): JSX.Element => {
  const [field, meta] = useField({ name })

  return (
    <>
      <label>
        {label}
        <textarea
          {...field}
          className={className}
          disabled={disabled}
          maxLength={maxLength}
          placeholder={placeholder}
        />
      </label>
      {meta.touched && meta.error ? (
        <div className="error">{meta.error}</div>
      ) : null}
    </>
  )
}

export default TextArea
