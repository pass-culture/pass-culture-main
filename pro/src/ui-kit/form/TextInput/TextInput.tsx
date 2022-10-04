import { useField } from 'formik'
import React, { ForwardedRef } from 'react'

import { BaseInput, FieldLayout } from '../shared'

import styles from './TextInput.module.scss'

interface ITextInputProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  name: string
  className?: string
  disabled?: boolean
  readOnly?: boolean
  hideFooter?: boolean
  label: string
  placeholder?: string
  type?: 'text' | 'number' | 'email' | 'url' | 'password' | 'tel'
  countCharacters?: boolean
  maxLength?: number
  isOptional?: boolean
  smallLabel?: boolean
  rightButton?: () => JSX.Element
  step?: number | string
  inline?: boolean
  refForInput?: ForwardedRef<HTMLInputElement>
}

const TextInput = ({
  name,
  type = 'text',
  className,
  disabled,
  readOnly,
  hideFooter,
  label,
  placeholder,
  countCharacters,
  maxLength,
  smallLabel,
  isOptional = false,
  refForInput,
  rightButton,
  step,
  inline = false,
  ...props
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
      hideFooter={hideFooter}
      isOptional={isOptional}
      label={label}
      maxLength={maxLength}
      name={name}
      showError={meta.touched && !!meta.error}
      smallLabel={smallLabel}
      inline={inline}
    >
      {readOnly ? (
        <span
          className={styles['text-input-readonly']}
          ref={refForInput}
          {...field}
          {...props}
        >
          {props.value}
        </span>
      ) : (
        <BaseInput
          disabled={disabled}
          hasError={meta.touched && !!meta.error}
          maxLength={maxLength}
          placeholder={placeholder}
          step={step}
          type={type}
          rightButton={rightButton}
          ref={refForInput}
          {...field}
          {...props}
        />
      )}
    </FieldLayout>
  )
}

export default TextInput
