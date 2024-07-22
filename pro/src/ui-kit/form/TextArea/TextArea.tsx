import cn from 'classnames'
import { useField } from 'formik'
import React from 'react'
import Textarea from 'react-autosize-textarea'

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
  placeholder,
  label,
  maxLength = 1000,
  countCharacters,
  isOptional,
  smallLabel,
  rows = 7,
}: TextAreaProps): JSX.Element => {
  const [field, meta] = useField({ name })

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
    >
      <Textarea
        aria-invalid={meta.touched && !!meta.error}
        className={cn(styles['text-area'], {
          [styles['has-error'] ?? '']: meta.touched && !!meta.error,
        })}
        disabled={disabled}
        id={name}
        rows={rows}
        maxLength={maxLength}
        placeholder={placeholder}
        aria-required={!isOptional}
        {...field}
      />
    </FieldLayout>
  )
}
