import cn from 'classnames'
import { useField } from 'formik'
import React, { useId } from 'react'

import { Tooltip } from 'ui-kit/Tooltip/Tooltip'

import styles from './IconRadio.module.scss'

interface IconRadioProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  name: string
  label: string
  icon: string | JSX.Element
  hasError?: boolean
  className?: string
}

export const IconRadio = ({
  name,
  value,
  label,
  icon,
  hasError,
  ...props
}: IconRadioProps): JSX.Element => {
  const id = useId()
  const [field] = useField({ name, value, type: 'radio' })

  return (
    <div className={styles['icon-radio']}>
      <label htmlFor={id} className={styles['icon-radio-label']}>
        {icon}
      </label>
      <Tooltip content={label}>
        <input
          {...field}
          type="radio"
          {...props}
          className={cn(styles['icon-radio-input'], {
            [styles['has-error']]: hasError,
            [styles['icon-radio-input-checked']]: field.checked,
            [styles['icon-radio-input-disabled']]: props.disabled,
          })}
          aria-invalid={hasError}
          id={id}
          checked={field.checked}
          disabled={props.disabled}
        />
      </Tooltip>
    </div>
  )
}
