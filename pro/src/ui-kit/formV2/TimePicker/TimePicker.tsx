import classNames from 'classnames'
import { ForwardedRef, forwardRef, useId } from 'react'

import { FieldError } from 'ui-kit/form/shared/FieldError/FieldError'
import { BaseTimePicker } from 'ui-kit/form/TimePicker/BaseTimePicker'
import { SuggestedTimeList } from 'ui-kit/form/TimePicker/types'

import styles from './TimePicker.module.scss'

type TimePickerProps = {
  disabled?: boolean
  value?: string
  onChange?: React.InputHTMLAttributes<HTMLInputElement>['onChange']
  onBlur?: React.FocusEventHandler<HTMLInputElement>
  /** Whether or not to display the asterisk in the label when the field is required */
  asterisk?: boolean
  /** Name of the input. Used for identifying it in an uncontrolled form, and for referencing the error */
  name: string
  className?: string
  label: string | React.ReactNode
  required?: boolean
  error?: string
  suggestedTimeList?: SuggestedTimeList
}

export const TimePicker = forwardRef(
  (
    {
      name,
      className,
      disabled,
      label,
      required,
      asterisk = true,
      error,
      value,
      onChange,
      onBlur,
      suggestedTimeList,
    }: TimePickerProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const labelId = useId()
    const errorId = useId()

    return (
      <div className={classNames(styles['time-picker'], className)}>
        <div className={styles['time-picker-field']}>
          <label htmlFor={labelId} className={styles['label']}>
            {label}
            {required && asterisk ? ' *' : ''}
          </label>
          <BaseTimePicker
            hasError={Boolean(error)}
            disabled={disabled}
            aria-required={required}
            value={value}
            ref={ref}
            onChange={onChange}
            onBlur={onBlur}
            name={name}
            id={labelId}
            aria-describedby={errorId}
            suggestedTimeList={suggestedTimeList}
          />
        </div>
        <div role="alert" id={errorId}>
          {error && (
            <FieldError name={name} className={styles['error']}>
              {error}
            </FieldError>
          )}
        </div>
      </div>
    )
  }
)

TimePicker.displayName = 'TimePicker'
