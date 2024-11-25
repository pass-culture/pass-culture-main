import cn from 'classnames'
import { useField } from 'formik'
import React, { useCallback } from 'react'

import { BaseRadio } from '../shared/BaseRadio/BaseRadio'

/**
 * Props for the RadioButton component.
 *
 * @extends Partial<React.InputHTMLAttributes<HTMLInputElement>>
 */
interface RadioButtonProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  /**
   * The name of the radio button field.
   */
  name: string
  /**
   * The label for the radio button.
   */
  label: string | JSX.Element
  /**
   * The value of the radio button.
   */
  value: string
  /**
   * Whether to add a border around the radio button.
   */
  withBorder?: boolean
  /**
   * Whether the radio button has an error.
   */
  hasError?: boolean
  /**
   * Whether the radio button should take up the full width of the container.
   */
  fullWidth?: boolean
  /**
   * ARIA attribute to describe the element the radio button is associated with.
   */
  ariaDescribedBy?: string
}

/**
 * The RadioButton component is a single radio button that integrates with Formik for form state management.
 * It can be customized with various layout and accessibility options.
 *
 * ---
 * **Important: Always use a meaningful label for accessibility.**
 * Labels are essential for screen readers and users who rely on assistive technology.
 * ---
 *
 * @param {RadioButtonProps} props - The props for the RadioButton component.
 * @returns {JSX.Element} The rendered RadioButton component.
 *
 * @example
 * <RadioButton
 *   name="gender"
 *   label="Male"
 *   value="male"
 *   withBorder={true}
 * />
 *
 * @accessibility
 * - **Labels**: Always provide a meaningful label using the `label` prop for screen readers. This helps users understand the purpose of the radio button.
 * - **Keyboard Accessibility**: Users can select the radio button using standard keyboard navigation (e.g., arrow keys).
 * - **ARIA Attributes**: Use `ariaDescribedBy` to link the radio button to additional descriptions or error messages, improving the user experience for screen reader users.
 */
export const RadioButton = ({
  disabled,
  name,
  label,
  value,
  withBorder,
  fullWidth,
  className,
  hasError,
  onChange,
  ariaDescribedBy,
}: RadioButtonProps): JSX.Element => {
  const [field] = useField({ name, value, type: 'radio' })

  const onCustomChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      field.onChange(e)
      if (onChange) {
        onChange(e)
      }
    },
    [field, onChange]
  )

  return (
    <BaseRadio
      {...field}
      disabled={disabled}
      id={name}
      label={label}
      value={value}
      className={cn(className)}
      checked={field.checked}
      hasError={hasError}
      withBorder={withBorder}
      fullWidth={fullWidth}
      onChange={(e) => onCustomChange(e)}
      ariaDescribedBy={ariaDescribedBy}
    />
  )
}
