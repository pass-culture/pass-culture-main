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
    countCharacters?: boolean
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
  countCharacters,
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

  return (
    <FieldLayout
      className={className}
      count={countCharacters ? field.value?.length : undefined}
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
        {...(description ? { 'aria-describedby': `description-${name}` } : {})}
        className={cn(styles['text-area'], {
          [styles['has-error']]: meta.touched && !!meta.error,
        })}
        disabled={disabled}
        id={name}
        rows={rows}
        maxLength={maxLength}
        placeholder={placeholder}
        aria-required={!isOptional}
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
