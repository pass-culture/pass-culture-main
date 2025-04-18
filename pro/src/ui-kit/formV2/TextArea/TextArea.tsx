import cn from 'classnames'
import React, {
  ForwardedRef,
  forwardRef,
  useEffect,
  useId,
  useImperativeHandle,
  useRef,
  useState,
} from 'react'

import { Button } from 'ui-kit/Button/Button'
import { FieldError } from 'ui-kit/form/shared/FieldError/FieldError'
import { FieldLayoutCharacterCount } from 'ui-kit/form/shared/FieldLayout/FieldLayoutCharacterCount/FieldLayoutCharacterCount'

import styles from './TextArea.module.scss'

/**
 * Props for the TextArea component.
 */
export type TextAreaProps = {
  /**
   * The name of the textarea field.
   */
  name: string
  /**
   * The initial number of visible text lines for the control. The field will still expand indefinitely if the input is higher than this value.
   * @default 7
   */
  initialRows?: number
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
   * Whether the textarea is disabled.
   */
  disabled?: boolean
  hasDefaultPlaceholder?: boolean
  /**
   * If the asterisk should be displayed when the field is required.
   */
  asterisk?: boolean
  /**
   * Error text displayed under the field. If the error is trythy, the field has the error styles.
   */
  error?: string
  onChange?: (e: { target: { value: string; name?: string } }) => void
  onBlur?: (e: React.FocusEvent<HTMLTextAreaElement>) => void
  value?: string
  /**
   * Count of characters typed in the field. If `undefined`, the counter is not displayed.
   */
  count?: boolean
} & (
  | {
      /**
       * Whether the template button should be displayed.
       */
      hasTemplateButton: boolean
      /**
       * Content of the templated added to the field when the template button is clicked
       */
      wordingTemplate: string
      /**
       * Callback after the template button is clicked.
       */
      onPressTemplateButton: () => void
    }
  | {
      hasTemplateButton?: false | undefined
      wordingTemplate?: never
      onPressTemplateButton?: never
    }
)

/**
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
      initialRows = 7,
      hasTemplateButton = false,
      wordingTemplate,
      hasDefaultPlaceholder,
      onPressTemplateButton,
      error,
      onChange,
      onBlur,
      value,
      count = true,
    }: TextAreaProps,
    ref: ForwardedRef<HTMLTextAreaElement>
  ) => {
    const textAreaRef = useRef<HTMLTextAreaElement>(null)

    const [textValue, setTextValue] = useState(value)

    const fieldId = useId()
    const descriptionId = useId()
    const errorId = useId()

    const countValue = textValue?.length ?? 0

    useImperativeHandle(ref, () => textAreaRef.current as HTMLTextAreaElement)

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
    }, [textValue])

    // Constructing aria-describedby attribute
    const describedBy = [`field-characters-count-description-${name}`, errorId]

    if (description) {
      describedBy.unshift(descriptionId)
    }

    const generateTemplate = () => {
      wordingTemplate && setTextValue(wordingTemplate)
      if (textAreaRef.current) {
        textAreaRef.current.focus()
        textAreaRef.current.setSelectionRange(128, 128)
      }
      onPressTemplateButton && onPressTemplateButton()
    }

    return (
      <div className={className}>
        <div className={styles['input-layout-label-container']}>
          <label className={styles['input-layout-label']} htmlFor={fieldId}>
            {label} {required && asterisk && '*'}
          </label>
          {description && (
            <span
              id={descriptionId}
              data-testid={`description-${name}`}
              className={styles['input-layout-input-description']}
            >
              {description}
            </span>
          )}
        </div>
        <div className={styles['wrapper']}>
          <textarea
            ref={textAreaRef}
            aria-invalid={!!error}
            aria-describedby={describedBy.join(' ')}
            className={cn(styles['text-area'], {
              [styles['has-error']]: !!error,
            })}
            disabled={disabled}
            id={fieldId}
            rows={initialRows}
            value={textValue}
            maxLength={maxLength}
            aria-required={!required}
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
          />
          {hasTemplateButton && (
            <Button
              className={styles['template-button']}
              onClick={generateTemplate}
              disabled={Boolean(textValue?.length)}
            >
              Générer un modèle
            </Button>
          )}
        </div>
        <div className={styles['input-layout-footer']}>
          <div role="alert" className={styles['error']} id={errorId}>
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
      </div>
    )
  }
)

TextArea.displayName = 'TextArea'
