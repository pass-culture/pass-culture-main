import { BaseRadio, FieldError } from '../shared'

import React from 'react'
import cn from 'classnames'
import style from './RadioButton.module.scss'
import { useField } from 'formik'

interface IRadioButtonProps {
  name: string
  label: string
  value: string
  className?: string
  checked?: boolean
  withBorder?: boolean
}

const RadioButton = ({
  name,
  label,
  value,
  withBorder,
  className,
}: IRadioButtonProps): JSX.Element => {
  const [field, meta] = useField({ name, value, type: 'radio' })

  return (
    <div
      className={cn(style['radio-button'], className, {
        [style['with-border']]: withBorder,
        [style['with-border-primary']]: withBorder && field.checked,
      })}
    >
      <BaseRadio
        {...field}
        id={name}
        label={label}
        value={value}
        className={cn(style['radio-input'], {
          [style['radio-input-checked']]: field.checked,
        })}
      />
      {meta.touched && meta.error && (
        <FieldError name={name}>{meta.error}</FieldError>
      )}
    </div>
  )
}

export default RadioButton
