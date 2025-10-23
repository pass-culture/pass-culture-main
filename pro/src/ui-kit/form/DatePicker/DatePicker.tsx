import classNames from 'classnames'
import React, { type ForwardedRef, useId } from 'react'

import { FieldFooter } from '@/design-system/common/FieldFooter/FieldFooter'
import { BaseDatePicker } from '@/ui-kit/form/shared/BaseDatePicker/BaseDatePicker'

import styles from './DatePicker.module.scss'

type DatePickerProps = {
  disabled?: boolean
  required?: boolean
  maxDate?: Date
  /** Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error */
  name: string
  label: string | React.ReactNode
  minDate?: Date
  onChange?: React.InputHTMLAttributes<HTMLInputElement>['onChange']
  onBlur?: React.FocusEventHandler<HTMLInputElement>
  /** Whether or not to display the asterisk in the label when the field is required */
  asterisk?: boolean
  error?: string
  value?: string
  className?: string
}

export const DatePicker = React.forwardRef(
  (
    {
      error,
      disabled,
      maxDate,
      minDate,
      onChange,
      required,
      onBlur,
      name,
      value,
      label,
      asterisk = true,
      className,
    }: DatePickerProps,
    ref: ForwardedRef<HTMLInputElement>
  ) => {
    const inputId = useId()
    const errorId = useId()

    return (
      <div className={classNames(styles['date-picker'], className)}>
        <div>
          <label htmlFor={inputId} className={styles['label']}>
            {label}
            {required && asterisk ? <>&nbsp;*</> : ''}
          </label>
          <BaseDatePicker
            data-testid={name}
            name={name}
            id={inputId}
            hasError={Boolean(error)}
            disabled={disabled}
            maxDate={maxDate}
            minDate={minDate}
            onChange={onChange}
            aria-required={required}
            onBlur={onBlur}
            value={value}
            aria-describedby={error ? errorId : undefined}
            ref={ref}
          />
        </div>
        <FieldFooter error={error} errorId={errorId} />
      </div>
    )
  }
)

DatePicker.displayName = 'DatePicker'
