import cn from 'classnames'
import { useField } from 'formik'
import React, { useEffect, useRef } from 'react'

import {
  FieldLayout,
  FieldLayoutBaseProps,
} from '../shared/FieldLayout/FieldLayout'

import styles from './TextArea.module.scss'

/**
 * Props for the TextArea component.
 *
 * @extends FieldLayoutBaseProps
 * @extends React.InputHTMLAttributes<HTMLTextAreaElement>
 */
type TextAreaProps = FieldLayoutBaseProps &
  React.InputHTMLAttributes<HTMLTextAreaElement> & {
    /**
     * The name of the textarea field.
     */
    name: string
    /**
     * The number of visible text lines for the control.
     * @default 7
     */
    rows?: number
    /**
     * The maximum number of characters allowed in the textarea.
     * @default 1000
     */
    maxLength?: number
    /**
     * Whether the field is optional.
     */
    isOptional?: boolean
    /**
     * The label text for the textarea.
     */
    label?: string | React.ReactNode
    /**
     * A description providing additional information about the textarea.
     */
    description?: string
    /**
     * Custom CSS class for the textarea component.
     */
    className?: string
    /**
     * Whether to display a smaller version of the label.
     */
    smallLabel?: boolean
    /**
     * Whether the textarea is disabled.
     */
    disabled?: boolean
    /**
     * The placeholder text for the textarea.
     *
     * **Important: Do not use the `placeholder` to indicate the format of the field.**
     * Use the `label` or `description` props instead to provide instructions on the expected format.
     */
    placeholder?: string
  }

/**
 * The TextArea component is a customizable textarea field that integrates with Formik for form state management.
 * It supports features like dynamic resizing based on content, character counting, and accessibility enhancements.
 *
 * ---
 * **Important: Do not use the `placeholder` to indicate the format of the field.**
 * Use the `label` or `description` props instead to provide instructions on the expected format.
 * ---
 *
 * @param {TextAreaProps} props - The props for the TextArea component.
 * @returns {JSX.Element} The rendered TextArea component.
 *
 * @example
 * <TextArea
 *   name="message"
 *   label="Your Message"
 *   description="Please enter your message."
 *   placeholder="Type your message here..."
 *   maxLength={500}
 * />
 *
 * @accessibility
 * - **Do not use the `placeholder` to indicate the format**: Placeholders are not always announced by screen readers and disappear once the user starts typing. Use `label` or `description` to provide information about the expected input.
 * - **Labels and ARIA**: Always provide the `label` prop so the field is correctly identified by assistive technologies. The component uses `aria-required` to indicate if the field is optional or required.
 * - **Descriptions**: If you use the `description` prop, it will be linked to the textarea via `aria-describedby`, providing additional information to users.
 * - **Character Counting**: The component displays the number of characters entered, helping users stay within the maximum allowed.
 * - **Dynamic Resizing**: The textarea automatically adjusts its height based on the content, improving usability.
 * - **Error Handling**: Error messages are handled and displayed in an accessible manner, informing users of issues with their input.
 * - **Keyboard Navigation**: Users can navigate and interact with the field using the keyboard, in compliance with accessibility standards.
 */
export const TextArea = ({
  name,
  className,
  disabled,
  description,
  placeholder,
  label,
  maxLength = 1000,
  isOptional,
  smallLabel,
  rows = 7,
  ...props
}: TextAreaProps): JSX.Element => {
  const [field, meta] = useField({ name })
  const textAreaRef = useRef<HTMLTextAreaElement>(null)

  /**
   * Updates the height of the textarea based on its content.
   * Resets the height to initial value before setting it to scrollHeight to allow shrinking.
   */
  function updateTextAreaHeight() {
    if (textAreaRef.current) {
      // Reset the textarea height to its initial value before reading the scrollHeight
      textAreaRef.current.style.height = 'unset'

      const scrollHeight = textAreaRef.current.scrollHeight
      textAreaRef.current.style.height = `${scrollHeight}px`
    }
  }

  useEffect(() => {
    // Set the textarea height after the first render to fit the initial content
    updateTextAreaHeight()
  }, [])

  // Constructing aria-describedby attribute
  const describedBy = [`field-characters-count-description-${name}`]

  if (description) {
    describedBy.unshift(`description-${name}`)
  }

  return (
    <FieldLayout
      className={className}
      count={field.value?.length}
      error={meta.error}
      isOptional={isOptional}
      label={label}
      maxLength={maxLength}
      name={name}
      showError={meta.touched && !!meta.error}
      smallLabel={smallLabel}
      description={description}
    >
      <textarea
        aria-invalid={meta.touched && !!meta.error}
        aria-describedby={describedBy.join(' ')}
        className={cn(styles['text-area'], {
          [styles['has-error']]: meta.touched && !!meta.error,
        })}
        disabled={disabled}
        id={name}
        rows={rows}
        maxLength={maxLength}
        placeholder={placeholder}
        aria-required={!isOptional}
        aria-controls={props['aria-controls']}
        ref={textAreaRef}
        {...field}
        onChange={(event) => {
          updateTextAreaHeight()
          field.onChange(event)
          props.onChange?.(event)
        }}
      />
    </FieldLayout>
  )
}
