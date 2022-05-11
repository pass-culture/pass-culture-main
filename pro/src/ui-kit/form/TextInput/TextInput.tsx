import { BaseInput, FieldLayout } from '../shared'

import React from 'react'
import { useField } from 'formik'

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
  rightButton?: () => JSX.Element
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
  rightButton,
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
        rightButton={rightButton}
        {...field}
      />
    </FieldLayout>
  )
}

export default TextInput
