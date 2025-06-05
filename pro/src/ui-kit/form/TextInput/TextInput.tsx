import { useField } from 'formik'
import React, { ForwardedRef } from 'react'

import { BaseInput, BaseInputProps } from '../shared/BaseInput/BaseInput'
import {
  FieldLayout,
  FieldLayoutBaseProps,
} from '../shared/FieldLayout/FieldLayout'

import styles from './TextInput.module.scss'

/**
 * Props for the TextInput component.
 *
 * @extends FieldLayoutBaseProps
 * @extends BaseInputProps
 */
export type TextInputProps = FieldLayoutBaseProps &
  BaseInputProps & {
    /**
     * A flag to make the input read-only.
     * It becomes a span element with the value displayed.
     * Only FieldLayout props, focusRef & value will then be used.
     */
    readOnly?: boolean
    /**
     * Allows displaying input characters count.
     * Must be provided with `maxLength` to be effective.
     * Adds `field-characters-count-description-${name}` to the `aria-describedby` attribute of the input.
     * Used for `FieldLayout` count prop.
     */
    countCharacters?: boolean
    /**
     * Allows decimal numbers in the input.
     * Must be provided with `type="number"` to be effective.
     * Unused when `readOnly` is true.
     * @default true
     */
    hasDecimal?: boolean
    /**
     * A forward ref to the span or the input element.
     */
    focusRef?: ForwardedRef<HTMLInputElement>
    /**
     * A custom error message to be displayed.
     * If this prop is provided, the error message will be displayed
     * and the field will be marked as errored regardless of the field's Formik state.
     * Used for `error` & `showError` `FieldLayout` props.
     */
    externalError?: string
    /**
     * A custom component to be displayed next to the input.
     * It can be used to display additional information or related actions like
     * a checkbox to reset the input value.
     */
    InputExtension?: React.ReactNode
  }

/**
 * The TextInput component is a customizable input field that integrates with Formik for form state management.
 * It supports features like character counting, read-only mode, decimal number input, and accessibility enhancements.
 *
 * ---
 * ** Important: Do not use the `placeholder` to indicate the format of the field.**
 * Use the `label` or `description` props instead to provide instructions on the expected format.
 * ---
 *
 * @param {TextInputProps} props - The props for the TextInput component.
 * @returns {JSX.Element} The rendered TextInput component.
 *
 * @example
 * <TextInput
 *   name="email"
 *   label="Email Address"
 *   description="Please enter a valid email address."
 *   isOptional
 * />
 *
 * @accessibility
 * - **Labels and ARIA**: Always provide the `label` prop so the field is correctly identified by assistive technologies. The component uses `aria-required` to indicate if the field is optional or required.
 * - **Descriptions**: If you use the `description` prop, it will be linked to the input via `aria-describedby`, providing additional information to users.
 * - **Character Counting**: When `countCharacters` is enabled, the number of characters entered is displayed, and a description is added for assistive technologies.
 * - **Error Handling**: Error messages are handled and displayed in an accessible manner, informing users of issues with their input.
 * - **Keyboard Navigation**: Users can navigate and interact with the field using the keyboard, in compliance with accessibility standards.
 */
export const TextInput = ({
  name,
  type = 'text',
  className,
  classNameFooter,
  classNameLabel,
  classNameInput,
  disabled,
  readOnly,
  label,
  isLabelHidden = false,
  countCharacters,
  maxLength = 255,
  isOptional = false,
  focusRef,
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
  hideAsterisk,
  InputExtension,
  ...props
}: TextInputProps): JSX.Element => {
  const [field, meta] = useField({
    name,
    type,
  })

  const showError = !!externalError || (meta.touched && !!meta.error)

  // Constructing aria-describedby attribute
  const describedBy = []

  if (description) {
    describedBy.push(`description-${name}`)
  }

  if (countCharacters) {
    describedBy.push(`field-characters-count-description-${name}`)
  }

  const input = (
    <BaseInput
      disabled={disabled}
      hasError={showError}
      maxLength={maxLength}
      step={step}
      type={type}
      rightButton={rightButton}
      ref={focusRef}
      rightIcon={rightIcon}
      leftIcon={leftIcon}
      aria-required={!isOptional}
      aria-describedby={describedBy.join(' ') || undefined}
      onKeyDown={(event) => {
        // If the number input should have no decimal, prevent the user from typing "," or "."
        if (type === 'number' && !hasDecimal && /[,.]/.test(event.key)) {
          event.preventDefault()
        }
      }}
      {...field}
      {...props}
    />
  )

  return (
    <FieldLayout
      className={className}
      classNameLabel={classNameLabel}
      classNameFooter={classNameFooter}
      classNameInput={classNameInput}
      count={countCharacters ? field.value.length : undefined}
      error={externalError || meta.error}
      isOptional={isOptional}
      hideAsterisk={hideAsterisk}
      label={label}
      isLabelHidden={isLabelHidden}
      maxLength={maxLength}
      name={name}
      showError={showError}
      inline={inline}
      description={description}
      clearButtonProps={clearButtonProps}
      ErrorDetails={ErrorDetails}
      hasLabelLineBreak={hasLabelLineBreak}
    >
      {readOnly ? (
        <span className={styles['text-input-readonly']} ref={focusRef}>
          {props.value}
        </span>
      ) : InputExtension ? (
        <div className={styles['text-input-group']} role="group">
          {input}
          <div className={styles['text-input-group-extension']}>
            {InputExtension}
          </div>
        </div>
      ) : (
        input
      )}
    </FieldLayout>
  )
}
