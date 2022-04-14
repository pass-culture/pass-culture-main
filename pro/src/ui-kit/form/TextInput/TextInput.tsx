import { useField } from 'formik'
import React from 'react'

import { BaseInput, FieldLayout } from '../shared'

interface ITextInputProps {
  name: string
  className?: string
  disabled?: boolean
  label: string
  placeholder?: string
  type?: 'text' | 'number' | 'email' | 'url' | 'password' | 'tel'
  countCharacters?: boolean
  maxLength?: number
  isOptional?: boolean
  smallLabel?: boolean
  step?: number | string
}

const TextInput = ({
  name,
  type = 'text',
  className,
  disabled,
  label,
  placeholder,
  countCharacters,
  maxLength,
  smallLabel,
  isOptional = false,
  step,
}: ITextInputProps): JSX.Element => {
  const [field, meta] = useField({
    name,
    type,
  })

  return (
    <FieldLayout
      className={className}
      count={countCharacters ? field.value.length : undefined}
      error={meta.error}
      isOptional={isOptional}
      label={label}
      maxLength={maxLength}
      name={name}
      showError={meta.touched && !!meta.error}
      smallLabel={smallLabel}
    >
      <BaseInput
        disabled={disabled}
        hasError={meta.touched && !!meta.error}
        maxLength={maxLength}
        placeholder={placeholder}
        step={step}
        type={type}
        {...field}
      />
    </FieldLayout>
  )
}

export default TextInput
