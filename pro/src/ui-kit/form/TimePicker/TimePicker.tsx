import cn from 'classnames'
import fr from 'date-fns/locale/fr'
import { useField } from 'formik'
import React from 'react'
import ReactDatePicker, { registerLocale } from 'react-datepicker'

import FieldError from '../FieldError'

import styles from './TimePicker.module.scss'
registerLocale('fr', fr)

interface DatePickerProps {
  name: string
  className?: string
  disabled?: boolean
  label?: string
  dateTime?: Date
}

const TimePicker = ({
  name,
  className,
  disabled,
  label,
}: DatePickerProps): JSX.Element => {
  const [field, meta, helpers] = useField({ name, type: 'text' })

  return (
    <div className={cn(styles['time-picker'], className)}>
      <label
        className={styles['time-picker-label']}
        htmlFor={`time-picker-${name}`}
      >
        {label}
      </label>
      <ReactDatePicker
        className="datetime-input"
        customInput={
          <input
            className={styles['time-picker-input']}
            id={`time-picker-${name}`}
            type="text"
            {...field}
          />
        }
        dateFormat="HH:mm"
        disabled={disabled}
        dropdownMode="scroll"
        locale="fr"
        onChange={time => helpers.setValue(time)}
        placeholderText="HH:MM"
        selected={field.value ?? null}
        showTimeSelect
        showTimeSelectOnly
        timeCaption="Horaire"
        timeFormat="HH:mm"
        timeIntervals={15}
      />

      {meta.touched && !!meta.error && <FieldError>{meta.error}</FieldError>}
    </div>
  )
}

export default TimePicker
