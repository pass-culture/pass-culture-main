import cn from 'classnames'
import React, { ForwardedRef } from 'react'

import {
  BaseInput,
  BaseInputProps,
} from 'ui-kit/form/shared/BaseInput/BaseInput'
import { FieldError } from 'ui-kit/form/shared/FieldError/FieldError'
import { FieldLayoutBaseProps } from 'ui-kit/form/shared/FieldLayout/FieldLayout'
import { FieldLayoutCharacterCount } from 'ui-kit/form/shared/FieldLayout/FieldLayoutCharacterCount/FieldLayoutCharacterCount'

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
     * If this prop is provided, the error message will be displayed and the field will be marked as errored
     */
    error?: string
    /**
     * A custom character counter to be displayed.
     * If this prop is provided, the counter will be displayed
     */
    count?: number
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
 *   required={true}
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
      disabled,
      readOnly,
      label,
      className,
      isLabelHidden = false,
      maxLength = 255,
      required = false,
      leftIcon,
      rightButton,
      rightIcon,
      hasDecimal = true,
      description,
      error,
      count,
      ...props
    }: TextInputProps,
    ref: ForwardedRef<HTMLInputElement>
  ) => {
    // Regex patterns for input validation
    const regexHasDecimal = /[0-9,.]/
    const regexHasNotDecimal = /[0-9]/
    const regexIsNavigationKey = /Tab|Backspace|Enter/

    const input = (
      <BaseInput
        name={name}
        disabled={disabled}
        hasError={!!error}
        maxLength={maxLength}
        type={type}
        ref={ref}
        rightButton={rightButton}
        rightIcon={rightIcon}
        leftIcon={leftIcon}
        aria-required={required}
        aria-describedby={description ? `description-${name}` : undefined}
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
      <div
        className={cn(styles['input-layout'], className)}
        data-testid={`wrapper-${name}`}
      >
        <div
          className={cn(styles['input-layout-label-container'], {
            [styles['visually-hidden']]: isLabelHidden,
          })}
        >
          <label className={styles['input-layout-label']} htmlFor={name}>
            {label} {required && '*'}
          </label>
          {description && (
            <span
              id={`description-${name}`}
              data-testid={`description-${name}`}
              className={styles['input-layout-input-description']}
            >
              {description}
            </span>
          )}
        </div>
        {readOnly ? (
          <span className={styles['text-input-readonly']}>{props.value}</span>
        ) : (
          <>
            <div className={styles['text-input']}>
              {input}
              <div className={styles['input-layout-footer']}>
                {error && (
                  <div
                    role="alert"
                    className={styles['input-layout-error']}
                    id={`error-details-${name}`}
                  >
                    <FieldError name={name}>{error}</FieldError>
                  </div>
                )}
                {count !== undefined && (
                  <FieldLayoutCharacterCount
                    count={count}
                    maxLength={maxLength}
                    name={name}
                  />
                )}
              </div>
            </div>
          </>
        )}
      </div>
    )
  }
)

TextInput.displayName = 'TextInput'
