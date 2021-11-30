import { useField } from 'formik'
import React from 'react'

import TextareaInput from 'components/layout/inputs/TextareaInput'

interface ITextAreaProps {
  name: string
  className?: string
  disabled?: boolean
  placeholder?: string
  label?: string
  maxLength?: number
  countCharacters?: boolean
}

const TextArea = ({
  name,
  className,
  disabled,
  placeholder,
  label,
  maxLength,
  countCharacters,
}: ITextAreaProps): JSX.Element => {
  const [field, meta] = useField({ name })

  return (
    <div className={className}>
      <TextareaInput
        countCharacters={countCharacters}
        disabled={disabled}
        error={meta.touched && !!meta.error ? meta.error : null}
        label={label}
        maxLength={maxLength}
        placeholder={placeholder}
        {...field}
      />
    </div>
  )
}

export default TextArea
