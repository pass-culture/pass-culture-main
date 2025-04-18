import cn from 'classnames'
import React, { ForwardedRef, forwardRef, useEffect, useState } from 'react'

import { useRemoteConfigParams } from 'app/App/analytics/firebase'
import { Button } from 'ui-kit/Button/Button'
import { FieldError } from 'ui-kit/form/shared/FieldError/FieldError'
import { FieldLayoutBaseProps } from 'ui-kit/form/shared/FieldLayout/FieldLayout'
import { FieldLayoutCharacterCount } from 'ui-kit/form/shared/FieldLayout/FieldLayoutCharacterCount/FieldLayoutCharacterCount'

import styles from './TextArea.module.scss'

/**
 * Props for the TextArea component.
 *
 * @extends FieldLayoutBaseProps
 * @extends React.InputHTMLAttributes<HTMLTextAreaElement>
 */
export type TextAreaProps = FieldLayoutBaseProps &
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
    required?: boolean
    /**
     * The label text for the textarea.
     */
    label: string | React.ReactNode
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
    isLabelHidden?: boolean
    asterisk?: boolean
    error?: string
    onChange?: (e: { target: { value: string; name?: string } }) => void
    onBlur?: (e: React.FocusEvent<HTMLTextAreaElement>) => void
    value?: string
    count?: boolean
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
export const TextArea = forwardRef<HTMLTextAreaElement, TextAreaProps>(
  (
    {
      name,
      className,
      disabled,
      description,
      label,
      maxLength = 1000,
      required = false,
      asterisk = true,
      smallLabel,
      rows = 7,
      hasTemplateButton = false,
      wordingTemplate,
      hasDefaultPlaceholder,
      onPressTemplateButton,
      isLabelHidden = false,
      error,
      onChange,
      onBlur,
      value,
      count = true,
      ...props
    }: TextAreaProps,
    ref: ForwardedRef<HTMLTextAreaElement>
  ) => {
    const [textValue, setTextValue] = useState(value)

    const countValue = textValue?.length ?? 0

    const {
      AB_COLLECTIVE_DESCRIPTION_TEMPLATE: isCollectiveDescriptionTemplateActive,
    } = useRemoteConfigParams()

    const shouldDisplayTemplateButton =
      hasTemplateButton && isCollectiveDescriptionTemplateActive === 'true'

    /**
     * Updates the height of the textarea based on its content.
     * Resets the height to initial value before setting it to scrollHeight to allow shrinking.
     */
    function updateTextAreaHeight() {
      if (ref && typeof ref === 'object' && ref.current) {
        // Reset the textarea height to its initial value before reading the scrollHeight
        ref.current.style.height = 'unset'

        const scrollHeight = ref.current.scrollHeight
        ref.current.style.height = `${hasTemplateButton ? scrollHeight + 92 : scrollHeight}px`
      }
    }

    useEffect(() => {
      // Set the textarea height after the first render to fit the initial content
      updateTextAreaHeight()
    }, [textValue])

    // Constructing aria-describedby attribute
    const describedBy = [`field-characters-count-description-${name}`]

    if (description) {
      describedBy.unshift(`description-${name}`)
    }

    const generateTemplate = () => {
      wordingTemplate && setTextValue(wordingTemplate)
      if (ref && typeof ref === 'object' && ref.current) {
        ref.current.focus()
        ref.current.setSelectionRange(128, 128)
      }
      onPressTemplateButton && onPressTemplateButton()
    }

    return (
      <div className={className}>
        <div
          className={cn(styles['input-layout-label-container'], {
            [styles['visually-hidden']]: isLabelHidden,
          })}
        >
          <label className={styles['input-layout-label']} htmlFor={name}>
            {label} {required && asterisk && '*'}
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
        <textarea
          ref={ref}
          aria-invalid={!!error}
          aria-describedby={describedBy.join(' ')}
          className={cn(styles['text-area'], {
            [styles['has-error']]: !!error,
          })}
          disabled={disabled}
          id={name}
          rows={rows}
          value={textValue}
          maxLength={maxLength}
          aria-required={!required}
          aria-controls={props['aria-controls']}
          placeholder={hasDefaultPlaceholder ? 'Écrivez ici...' : undefined}
          onChange={(event) => {
            setTextValue(event.target.value)
            if (onChange) {
              onChange({
                ...event,
                target: { ...event.target, value: event.target.value, name },
              })
            }
          }}
          onBlur={(event) => {
            setTextValue(event.target.value)
            if (onBlur) {
              onBlur({
                ...event,
                target: { ...event.target, value: event.target.value, name },
              })
            }
          }}
          {...props}
        />
        <div className={styles['input-layout-footer']}>
          <div
            role="alert"
            className={styles['input-layout-error']}
            id={`error-details-${name}`}
          >
            {error && <FieldError name={name}>{error}</FieldError>}
          </div>

          {count && (
            <FieldLayoutCharacterCount
              count={countValue}
              maxLength={maxLength}
              name={name}
            />
          )}
        </div>
        {shouldDisplayTemplateButton && (
          <Button
            className={styles['template-button']}
            onClick={generateTemplate}
            disabled={Boolean(textValue?.length)}
          >
            Générer un modèle
          </Button>
        )}
      </div>
    )
  }
)

TextArea.displayName = 'TextArea'
