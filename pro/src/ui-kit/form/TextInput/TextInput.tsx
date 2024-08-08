import { useField } from 'formik'
import React, { ForwardedRef } from 'react'

import { BaseInput } from '../shared/BaseInput/BaseInput'
import {
  FieldLayout,
  FieldLayoutBaseProps,
} from '../shared/FieldLayout/FieldLayout'

import styles from './TextInput.module.scss'

type TextInputProps = React.InputHTMLAttributes<HTMLInputElement> &
  FieldLayoutBaseProps & {
    readOnly?: boolean
    type?: 'text' | 'number' | 'email' | 'url' | 'password' | 'tel' | 'search'
    countCharacters?: boolean
    leftIcon?: string
    rightButton?: () => JSX.Element
    rightIcon?: string
    step?: number | string
    hasDecimal?: boolean
    refForInput?: ForwardedRef<HTMLInputElement>
    ErrorDetails?: React.ReactNode
    maxLength?: number
  }

export const TextInput = ({
  name,
  type = 'text',
  className,
  classNameFooter,
  classNameLabel,
  classNameInput,
  disabled,
  readOnly,
  hideFooter,
  label,
  isLabelHidden = false,
  placeholder,
  countCharacters,
  maxLength = 255,
  smallLabel,
  isOptional = false,
  refForInput,
  leftIcon,
  rightButton,
  rightIcon,
  step,
  hasDecimal = true,
  inline = false,
  description,
  clearButtonProps,
  hasLabelLineBreak = true,
  ErrorDetails,
  ...props
}: TextInputProps): JSX.Element => {
  const [field, meta] = useField({
    name,
    type,
  })

  // think to add step="0.01" for decimal fields
  const regexHasDecimal = /[0-9,.]/
  const regexHasNotDecimal = /[0-9]/
  const regexIsNavigationKey = /Tab|Backspace|Enter/
  const showError = meta.touched && !!meta.error

  return (
    <FieldLayout
      className={className}
      classNameLabel={classNameLabel}
      classNameFooter={classNameFooter}
      classNameInput={classNameInput}
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
      ErrorDetails={ErrorDetails}
      hasLabelLineBreak={hasLabelLineBreak}
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
          leftIcon={leftIcon}
          aria-required={!isOptional}
          {...(description
            ? { 'aria-describedby': `description-${name}` }
            : {})}
          onKeyDown={(event) => {
            if (type === 'number') {
              if (regexIsNavigationKey.test(event.key)) {
                return
              }
              const testInput = hasDecimal
                ? !regexHasDecimal.test(event.key)
                : !regexHasNotDecimal.test(event.key)
              testInput && event.preventDefault()
            }
          }}
          // Disable changing input value on scroll over a number input
          onWheel={(event) => {
            if (type === 'number') {
              // We blur so that the input loses focus and the scroll still happens on the page
              // otherwise the user can't scroll the page if the cursor is over the input
              event.currentTarget.blur()
            }
          }}
          {...field}
          {...props}
        />
      )}
    </FieldLayout>
  )
}
