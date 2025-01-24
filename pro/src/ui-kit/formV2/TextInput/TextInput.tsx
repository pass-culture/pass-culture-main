import React, { ForwardedRef } from 'react'

import {
  BaseInput,
  BaseInputProps,
} from 'ui-kit/form/shared/BaseInput/BaseInput'
import {
  FieldLayout,
  FieldLayoutBaseProps,
} from 'ui-kit/form/shared/FieldLayout/FieldLayout'

import styles from './TextInput.module.scss'

/**
 * Props for the TextInput component.
 *
 * @extends FieldLayoutBaseProps
 * @extends BaseInputProps
 */
type TextInputProps = FieldLayoutBaseProps &
  BaseInputProps & {
    readOnly?: boolean
    /**
     * Allows decimal numbers in the input.
     * Must be provided with `type="number"` to be effective.
     * Unused when `readOnly` is true.
     * @default true
     */
    hasDecimal?: boolean
    /**
     * A custom error message to be displayed.
     * If this prop is provided, the error message will be displayed
     * and the field will be marked as errored regardless of the field's Formik state.
     * Used for `error` & `showError` `FieldLayout` props.
     */
    error?: string
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
 * - **Do not use the `placeholder` to indicate the format**: Placeholders are not always announced by screen readers and disappear once the user starts typing. Use `label` or `description` to provide information about the expected format.
 * - **Labels and ARIA**: Always provide the `label` prop so the field is correctly identified by assistive technologies. The component uses `aria-required` to indicate if the field is optional or required.
 * - **Descriptions**: If you use the `description` prop, it will be linked to the input via `aria-describedby`, providing additional information to users.
 * - **Error Handling**: Error messages are handled and displayed in an accessible manner, informing users of issues with their input.
 * - **Keyboard Navigation**: Users can navigate and interact with the field using the keyboard, in compliance with accessibility standards.
 */

export const TextInput = React.forwardRef(
  (
    {
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
      maxLength = 255,
      smallLabel,
      isOptional = false,
      leftIcon,
      rightButton,
      rightIcon,
      step,
      hasDecimal = true,
      inline = false,
      description,
      clearButtonProps,
      hasLabelLineBreak = true,
      error,
      showMandatoryAsterisk,
      InputExtension,
      ...props
    }: TextInputProps,
    ref: ForwardedRef<HTMLInputElement>
  ) => {
    // Regex patterns for input validation
    const regexHasDecimal = /[0-9,.]/
    const regexHasNotDecimal = /[0-9]/
    const regexIsNavigationKey = /Tab|Backspace|Enter/
    const showError = !!error

    // Constructing aria-describedby attribute
    const describedBy = []

    if (description) {
      describedBy.push(`description-${name}`)
    }

    const input = (
      <BaseInput
        name={name}
        disabled={disabled}
        hasError={showError}
        maxLength={maxLength}
        step={step}
        type={type}
        ref={ref}
        rightButton={rightButton}
        rightIcon={rightIcon}
        leftIcon={leftIcon}
        aria-required={!isOptional}
        aria-describedby={describedBy.join(' ') || undefined}
        onKeyDown={(event) => {
          // Restrict input for number types
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
        /* istanbul ignore next */
        onWheel={(event) => {
          /* istanbul ignore next */
          if (type === 'number') {
            // Blur the input to prevent value change on scroll
            /* istanbul ignore next */
            event.currentTarget.blur()
          }
        }}
        {...props}
      />
    )

    return (
      <FieldLayout
        className={className}
        classNameLabel={classNameLabel}
        classNameFooter={classNameFooter}
        classNameInput={classNameInput}
        error={error}
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
        hasLabelLineBreak={hasLabelLineBreak}
      >
        {readOnly ? (
          <span className={styles['text-input-readonly']}>{props.value}</span>
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
)

TextInput.displayName = 'TextInput'
