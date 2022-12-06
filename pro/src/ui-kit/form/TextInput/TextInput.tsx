import { useField } from 'formik'
import React, { ForwardedRef } from 'react'

import { BaseInput, FieldLayout } from '../shared'

import styles from './TextInput.module.scss'

export interface ITextInputProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  name: string
  className?: string
  classNameLabel?: string
  classNameFooter?: string
  disabled?: boolean
  readOnly?: boolean
  hideFooter?: boolean
  label: string
  isLabelHidden?: boolean
  placeholder?: string
  type?: 'text' | 'number' | 'email' | 'url' | 'password' | 'tel'
  countCharacters?: boolean
  maxLength?: number
  isOptional?: boolean
  smallLabel?: boolean
  rightButton?: () => JSX.Element
  rightIcon?: () => JSX.Element | null
  step?: number | string
  inline?: boolean
  refForInput?: ForwardedRef<HTMLInputElement>
  onlyNumbers?: boolean
}

const TextInput = ({
  name,
  type = 'text',
  className,
  classNameFooter,
  classNameLabel,
  disabled,
  readOnly,
  hideFooter,
  label,
  isLabelHidden = false,
  placeholder,
  countCharacters,
  maxLength,
  smallLabel,
  isOptional = false,
  refForInput,
  rightButton,
  rightIcon,
  step,
  inline = false,
  onlyNumbers = false,
  ...props
}: ITextInputProps): JSX.Element => {
  const [field, meta] = useField({
    name,
    type,
  })

  return (
    <FieldLayout
      className={className}
      classNameLabel={classNameLabel}
      classNameFooter={classNameFooter}
      count={countCharacters ? field.value.length : undefined}
      error={meta.error}
      hideFooter={hideFooter}
      isOptional={isOptional}
      label={label}
      isLabelHidden={isLabelHidden}
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
          rightIcon={rightIcon}
          onKeyPress={event => {
            if (onlyNumbers) {
              !/[0-9]|Backspace/.test(event.key) && event.preventDefault()
            }
          }}
          {...field}
          {...props}
        />
      )}
    </FieldLayout>
  )
}

export default TextInput
