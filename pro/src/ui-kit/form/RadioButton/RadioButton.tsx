import cn from 'classnames'
import { useField } from 'formik'
import React from 'react'

import { FieldError, BaseRadio } from '../shared'

import style from './RadioButton.module.scss'

interface IRadioButtonProps {
  name: string
  label: string
  value: string
  className?: string
  checked?: boolean
}

const RadioButton = ({
  name,
  label,
  value,
  className,
}: IRadioButtonProps): JSX.Element => {
  const [field, meta] = useField({ name, value, type: 'radio' })

  return (
    <div className={cn(style['radio-button'], className)}>
      <BaseRadio {...field} label={label} value={value} />
      {meta.touched && meta.error && (
        <FieldError name={name}>{meta.error}</FieldError>
      )}
    </div>
  )
}

export default RadioButton
