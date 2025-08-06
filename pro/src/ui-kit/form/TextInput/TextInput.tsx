import cn from 'classnames'
import React, { ForwardedRef, useId } from 'react'

import {
  BaseInput,
  BaseInputProps,
} from '@/ui-kit/form/shared/BaseInput/BaseInput'
import { FieldError } from '@/ui-kit/form/shared/FieldError/FieldError'
import { FieldLayoutBaseProps } from '@/ui-kit/form/shared/FieldLayout/FieldLayout'
import { FieldLayoutCharacterCount } from '@/ui-kit/form/shared/FieldLayout/FieldLayoutCharacterCount/FieldLayoutCharacterCount'

import styles from './TextInput.module.scss'

/**
 * Props for the TextInput component.
 *
 * @extends FieldLayoutBaseProps
 * @extends BaseInputProps
 */
export type TextInputProps = FieldLayoutBaseProps &
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
    /**
     * A property to not displayed asterisk even if field is required
     * If this prop is provided, the asterisk will not be displayed
     */
    asterisk?: boolean
    /**
     * A custom component to be displayed next to the input.
     * It can be used to display additional information or related actions like
     * a checkbox to reset the input value.
     */
    InputExtension?: React.ReactNode
    /**
     * An extra class name to be applied to the label element.
     * This can be used to customize the label's appearance.
     */
    labelClassName?: string
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
      labelClassName,
      isLabelHidden = false,
      maxLength = 255,
      required = false,
      asterisk = true,
      leftIcon,
      rightButton,
      rightIcon,
      hasDecimal = true,
      description,
      error,
      count,
      InputExtension,
      ...props
    }: TextInputProps,
    ref: ForwardedRef<HTMLInputElement>
  ) => {
    const errorId = useId()
    const descriptionId = useId()

    const describedBy = `${error ? errorId : ''}${description ? ` ${descriptionId}` : ''}`

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
        aria-describedby={describedBy}
        onKeyDown={(event) => {
          // If the number input should have no decimal, prevent the user from typing "," or "."
          if (type === 'number' && !hasDecimal && /[,.]/.test(event.key)) {
            event.preventDefault()
          }
        }}
        {...props}
      />
    )

    //  The footer must remain in the DOM because elements will role "alert" and "status"
    //  should already be in the DOM when their content changes. But the display of the footer div
    //  must change when it's empty so that the grid does not add unnecessary gaps.
    const hasFooter = error || count !== undefined

    return (
      <div
        className={cn(
          styles['grid-layout-input-container'],
          { [styles['has-footer']]: hasFooter },
          className
        )}
        data-testid={`wrapper-${name}`}
      >
        <div className={styles['grid-layout-label']}>
          <div
            className={cn({
              [styles['visually-hidden']]: isLabelHidden,
            })}
          >
            <label className={labelClassName} htmlFor={name}>
              {label} {required && asterisk && '*'}
            </label>
            {description && (
              <span
                id={`description-${name}`}
                data-testid={`description-${name}`}
                className={styles['grid-layout-label-description']}
              >
                {description}
              </span>
            )}
          </div>
        </div>
        {readOnly ? (
          <span className={cn(styles['grid-layout-input'])}>{props.value}</span>
        ) : (
          <>
            <div className={styles['grid-layout-input']}>{input}</div>
            <div className={styles['grid-layout-footer']}>
              <div role="alert" id={errorId}>
                {error && (
                  <FieldError
                    name={name}
                    className={styles['input-layout-error']}
                  >
                    {error}
                  </FieldError>
                )}
              </div>

              {count !== undefined && (
                <FieldLayoutCharacterCount
                  count={count}
                  maxLength={maxLength}
                  name={name}
                />
              )}
            </div>
            {InputExtension && (
              <div className={styles['grid-input-extension']}>
                {InputExtension}
              </div>
            )}
          </>
        )}
      </div>
    )
  }
)

TextInput.displayName = 'TextInput'
