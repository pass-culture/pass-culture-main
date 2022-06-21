import { BaseRadio } from '../shared'

import React from 'react'
import cn from 'classnames'
import style from './RadioButton.module.scss'
import { useField } from 'formik'

interface IRadioButtonProps {
  disabled?: boolean
  name: string
  label: string
  value: string
  className?: string
  checked?: boolean
  withBorder?: boolean
}

const RadioButton = ({
  disabled,
  name,
  label,
  value,
  withBorder,
  className,
}: IRadioButtonProps): JSX.Element => {
  const [field] = useField({ name, value, type: 'radio' })

  return (
    <div
      className={cn(style['radio-button'], className, {
        [style['with-border']]: withBorder,
        [style['with-border-primary']]: withBorder && field.checked,
      })}
    >
      <BaseRadio
        {...field}
        disabled={disabled}
        id={name}
        label={label}
        value={value}
        className={cn(style['radio-input'], {
          [style['radio-input-checked']]: field.checked,
        })}
        checked={field.checked}
      />
    </div>
  )
}

export default RadioButton
