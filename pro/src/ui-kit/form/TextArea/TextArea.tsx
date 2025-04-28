import cn from 'classnames'
import { useField } from 'formik'
import React, { useEffect, useRef } from 'react'

import { Button } from 'ui-kit/Button/Button'

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
  Omit<React.InputHTMLAttributes<HTMLTextAreaElement>, 'placeholder'> & {
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
    hasDefaultPlaceholder?: boolean
  } & (
    | {
        hasTemplateButton: boolean
        wordingTemplate: string
        onPressTemplateButton: () => void
      }
    | {
        hasTemplateButton?: false | undefined
        wordingTemplate?: never
        onPressTemplateButton?: never
      }
  )

/**
 * The TextArea component is a customizable textarea field that integrates with Formik for form state management.
 * It supports features like dynamic resizing based on content, character counting, and accessibility enhancements.
 *
 * @param {TextAreaProps} props - The props for the TextArea component.
 * @returns {JSX.Element} The rendered TextArea component.
 *
 * @example
 * <TextArea
 *   name="message"
 *   label="Your Message"
 *   description="Please enter your message."
 *   maxLength={500}
 * />
 *
 * @accessibility
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
  label,
  maxLength = 1000,
  isOptional,
  smallLabel,
  rows = 7,
  hasTemplateButton = false,
  wordingTemplate,
  hasDefaultPlaceholder,
  onPressTemplateButton,
  ...props
}: TextAreaProps): JSX.Element => {
  const [field, meta, helpers] = useField({ name })
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
      textAreaRef.current.style.height = `${hasTemplateButton ? scrollHeight + 92 : scrollHeight}px`
    }
  }

  useEffect(() => {
    // Set the textarea height after the first render to fit the initial content
    updateTextAreaHeight()
  }, [field.value])

  // Constructing aria-describedby attribute
  const describedBy = [`field-characters-count-description-${name}`]

  if (description) {
    describedBy.unshift(`description-${name}`)
  }

  const generateTemplate = async () => {
    await helpers.setValue(wordingTemplate)
    if (textAreaRef.current) {
      textAreaRef.current.focus()
      textAreaRef.current.setSelectionRange(128, 128)
    }
    onPressTemplateButton && onPressTemplateButton()
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
      hideAsterisk={props.hideAsterisk}
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
        aria-required={!isOptional}
        aria-controls={props['aria-controls']}
        ref={textAreaRef}
        {...field}
        placeholder={hasDefaultPlaceholder ? 'Écrivez ici...' : undefined}
        onChange={(event) => {
          field.onChange(event)
          props.onChange?.(event)
        }}
      />
      {hasTemplateButton && (
        <Button
          className={styles['template-button']}
          onClick={generateTemplate}
          disabled={field.value?.length}
        >
          Générer un modèle
        </Button>
      )}
    </FieldLayout>
  )
}
