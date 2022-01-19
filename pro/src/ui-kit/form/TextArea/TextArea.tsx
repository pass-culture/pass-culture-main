import cn from 'classnames'
import { useField } from 'formik'
import React from 'react'
import Textarea from 'react-autosize-textarea'

import { FieldLayout } from '../shared'

import styles from './TextArea.module.scss'

interface ITextAreaProps {
  name: string
  className?: string
  disabled?: boolean
  placeholder?: string
  label: string
  maxLength?: number
  countCharacters?: boolean
  isOptional?: boolean
  smallLabel?: boolean
}

const TextArea = ({
  name,
  className,
  disabled,
  placeholder,
  label,
  maxLength,
  countCharacters,
  isOptional,
  smallLabel,
}: ITextAreaProps): JSX.Element => {
  const [field, meta] = useField({ name })

  return (
    <FieldLayout
      className={className}
      count={countCharacters ? field.value.length : undefined}
      error={meta.error}
      isOptional={isOptional}
      label={label}
      maxLength={maxLength}
      name={name}
      showError={meta.touched && !!meta.error}
      smallLabel={smallLabel}
    >
      <Textarea
        aria-invalid={meta.touched && !!meta.error}
        className={cn(styles['text-area'], {
          [styles['has-error']]: meta.touched && !!meta.error,
        })}
        disabled={disabled}
        id={name}
        maxLength={maxLength}
        placeholder={placeholder}
        {...field}
      />
    </FieldLayout>
  )
}

export default TextArea
