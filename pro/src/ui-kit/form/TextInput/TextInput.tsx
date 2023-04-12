import { useField } from 'formik'
import React, { ForwardedRef } from 'react'

import { BaseInput, FieldLayout } from '../shared'
import { FieldLayoutBaseProps } from '../shared/FieldLayout/FieldLayout'

import styles from './TextInput.module.scss'

export type TextInputProps = React.InputHTMLAttributes<HTMLInputElement> &
  FieldLayoutBaseProps & {
    readOnly?: boolean
    type?: 'text' | 'number' | 'email' | 'url' | 'password' | 'tel'
    countCharacters?: boolean
    rightButton?: () => JSX.Element
    rightIcon?: () => JSX.Element
    step?: number | string
    hasDecimal?: boolean
    refForInput?: ForwardedRef<HTMLInputElement>
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
  hasDecimal = true,
  inline = false,
  description,
  clearButtonProps,
  ...props
}: TextInputProps): JSX.Element => {
  const [field, meta] = useField({
    name,
    type,
  })

  // think to add step="0.01" for decimal fields
  const regexHasDecimal = /[0-9,.]|Backspace|Enter/
  const regexHasNotDecimal = /[0-9]|Backspace|Enter/
  const showError = meta.touched && !!meta.error

  return (
    <FieldLayout
      className={className}
      classNameLabel={classNameLabel}
      classNameFooter={classNameFooter}
      count={countCharacters ? field.value.length : undefined}
      error={meta.error}
      isOptional={isOptional}
      label={label}
      isLabelHidden={isLabelHidden}
      maxLength={maxLength}
      name={name}
      showError={showError}
      smallLabel={smallLabel}
      inline={inline}
      hideFooter={hideFooter}
      description={description}
      clearButtonProps={clearButtonProps}
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
            if (type === 'number') {
              const testInput = hasDecimal
                ? !regexHasDecimal.test(event.key)
                : !regexHasNotDecimal.test(event.key)
              testInput && event.preventDefault()
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
