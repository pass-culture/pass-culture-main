import cn from 'classnames'
import { useField } from 'formik'
import { useEffect, useRef } from 'react'

import {
  FieldLayout,
  FieldLayoutBaseProps,
} from '../shared/FieldLayout/FieldLayout'

import styles from './TextArea.module.scss'

type TextAreaProps = React.InputHTMLAttributes<HTMLTextAreaElement> &
  FieldLayoutBaseProps & {
    rows?: number
    maxLength?: number
  }

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

  function updateTextAreaHeight() {
    if (textAreaRef.current) {
      //  Reset the textArea height to its initial value based on the 'rows' props before reading the scrollHeight
      //  so that the input is able to shrink back to its smallest height
      textAreaRef.current.style.height = `unset`

      const scrollHeight = textAreaRef.current.scrollHeight
      textAreaRef.current.style.height = `${scrollHeight}px`
    }
  }

  useEffect(() => {
    //  After the first render, set the textarea height to avoid having to scroll within the input with the current field value
    updateTextAreaHeight()
  }, [])

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
