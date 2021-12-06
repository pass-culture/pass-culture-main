import cn from 'classnames'
import { useField } from 'formik'
import React from 'react'

import { default as LayoutTextInput } from 'components/layout/inputs/TextInput/TextInput'

import styles from './TextInput.module.scss'

interface ITextInputProps {
  name: string
  className?: string
  disabled?: boolean
  label?: string
  placeholder?: string
  type?: 'text' | 'number'
  countCharacters?: boolean
  maxLength?: number
  required?: boolean
}

const TextInput = ({
  name,
  type = 'text',
  className,
  disabled,
  label,
  placeholder,
  countCharacters,
  maxLength,
  required,
}: ITextInputProps): JSX.Element => {
  const [field, meta] = useField({ name, disabled })

  return (
    <div className={cn(styles['text-input'], className)}>
      <LayoutTextInput
        countCharacters={countCharacters}
        error={meta.touched && !!meta.error ? meta.error : null}
        label={label ?? ''}
        maxLength={maxLength}
        placeholder={placeholder}
        required={required}
        type={type}
        {...field}
      />
    </div>
  )
}

export default TextInput
