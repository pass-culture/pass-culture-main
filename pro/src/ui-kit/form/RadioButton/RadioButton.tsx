import cn from 'classnames'
import { useField } from 'formik'
import React from 'react'

import { BaseRadio } from '../shared'

import style from './RadioButton.module.scss'

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
      className={cn(className, {
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
