import cn from 'classnames'
import { ForwardedRef, forwardRef, useId } from 'react'

import { Tooltip } from 'ui-kit/Tooltip/Tooltip'

import styles from './IconRadio.module.scss'

interface IconRadioProps {
  name: string
  label: string
  icon: string | JSX.Element
  hasError?: boolean
  className?: string
  checked?: boolean
  disabled?: boolean
  onChange?: React.InputHTMLAttributes<HTMLInputElement>['onChange']
  onBlur?: React.InputHTMLAttributes<HTMLInputElement>['onBlur']
}

export const IconRadio = forwardRef(
  (
    {
      name,
      label,
      icon,
      hasError,
      checked,
      disabled,
      onChange,
      onBlur,
    }: IconRadioProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const labelId = useId()

    return (
      <div className={styles['icon-radio']}>
        <label htmlFor={labelId} className={styles['icon-radio-label']}>
          {label}
        </label>
        <div className={styles['icon-radio-icon']}>{icon}</div>
        <Tooltip content={label}>
          <input
            type="radio"
            id={labelId}
            className={cn(styles['icon-radio-input'], {
              [styles['has-error']]: hasError,
              [styles['icon-radio-input-checked']]: checked,
            })}
            aria-invalid={hasError}
            checked={checked}
            disabled={disabled}
            name={name}
            onChange={onChange}
            onBlur={onBlur}
            ref={ref}
          />
        </Tooltip>
      </div>
    )
  }
)

IconRadio.displayName = 'IconRadio'
