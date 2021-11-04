import { useField } from 'formik'
import React from 'react'

interface ITextAreaProps {
  name: string;
  className?: string;
  disabled?: boolean;
  label?: string;
}

const TextArea = ({
  name,
  className,
  disabled,
  label,
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
        />
      </label>
      {meta.touched && meta.error ? (
        <div className="error">
          {meta.error}
        </div>
      ) : null}
    </>
  )
}

export default TextArea
