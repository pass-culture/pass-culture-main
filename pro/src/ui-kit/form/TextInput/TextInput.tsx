import { useField } from 'formik'
import React, { ForwardedRef } from 'react'

import { BaseInput, BaseInputProps } from '../shared/BaseInput/BaseInput'
import {
  FieldLayout,
  FieldLayoutBaseProps,
} from '../shared/FieldLayout/FieldLayout'

import styles from './TextInput.module.scss'

export type TextInputProps = FieldLayoutBaseProps &
  BaseInputProps & {
    /**
     * A flag to make the input read-only.
     * It becomes a span element with the value displayed.
     * Only FieldLayout props, refForInput & value will then
     * be used.
     */
    readOnly?: boolean
    /**
     * Allows to display input characters count.
     * Must be provided with maxLength to be effective,
     * Adds `field-characters-count-description-${name}`
     * to the aria-describedby attribute of the input.
     * Used for FieldLayout count prop.
     */
    countCharacters?: boolean
    /**
     * Allows decimal numbers in the input.
     * Must be provided with type="number" to be effective.
     * Unused when readOnly is true.
     */
    hasDecimal?: boolean
    /**
     * A forward ref to the span or the input element.
     */
    refForInput?: ForwardedRef<HTMLInputElement>
    /**
     * A custom error message to be displayed.
     * If this prop is provided, the error message will be displayed
     * and the field will be marked as errored
     * regardless of the field's formik state.
     * Used for error & showError FieldLayout props.
     */
    externalError?: string
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
  externalError,
  ErrorDetails,
  showMandatoryAsterisk,
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
  const showError = !!externalError || (meta.touched && !!meta.error)

  const describedBy = []

  if (description) {
    describedBy.push(`description-${name}`)
  }

  if (countCharacters) {
    describedBy.push(`field-characters-count-description-${name}`)
  }

  return (
    <FieldLayout
      className={className}
      classNameLabel={classNameLabel}
      classNameFooter={classNameFooter}
      classNameInput={classNameInput}
      count={countCharacters ? field.value.length : undefined}
      error={externalError || meta.error}
      isOptional={isOptional}
      showMandatoryAsterisk={showMandatoryAsterisk}
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
        <span className={styles['text-input-readonly']} ref={refForInput}>
          {props.value}
        </span>
      ) : (
        <BaseInput
          disabled={disabled}
          hasError={showError}
          maxLength={maxLength}
          placeholder={placeholder}
          step={step}
          type={type}
          rightButton={rightButton}
          ref={refForInput}
          rightIcon={rightIcon}
          leftIcon={leftIcon}
          aria-required={!isOptional}
          aria-describedby={describedBy.join(' ') || undefined}
          onKeyDown={(event) => {
            if (type === 'number') {
              if (regexIsNavigationKey.test(event.key)) {
                return
              }
              const testInput = hasDecimal
                ? !regexHasDecimal.test(event.key)
                : !regexHasNotDecimal.test(event.key)
              if (testInput) {
                event.preventDefault()
              }
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
