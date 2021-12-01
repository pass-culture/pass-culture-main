import cn from 'classnames'
import fr from 'date-fns/locale/fr'
import { useField } from 'formik'
import React from 'react'
import { default as ReactDatePicker, registerLocale } from 'react-datepicker'

import FieldError from '../FieldError'

import styles from './DatePicker.module.scss'

registerLocale('fr', fr)

interface DatePickerProps {
  name: string
  className?: string
  disabled?: boolean
  label?: string
  maxDateTime?: Date
  minDateTime?: Date
  openingDateTime?: Date
  dateTime?: Date
}

const DatePicker = ({
  name,
  maxDateTime,
  minDateTime,
  openingDateTime,
  className,
  disabled,
  label,
}: DatePickerProps): JSX.Element => {
  const [field, meta, helpers] = useField({ name, type: 'date' })

  return (
    <div className={cn(styles['date-picker'], className)}>
      <label
        className={styles['date-picker-label']}
        htmlFor={`datepicker-${name}`}
      >
        {label}
      </label>
      <ReactDatePicker
        className="datetime-input"
        customInput={
          <input
            className={styles['date-picker-input']}
            id={`datepicker-${name}`}
            type="date"
            {...field}
          />
        }
        dateFormat="dd/MM/yyyy"
        disabled={disabled}
        dropdownMode="scroll"
        locale="fr"
        maxDate={maxDateTime}
        minDate={minDateTime}
        onChange={date => helpers.setValue(date)}
        openToDate={field.value ? field.value : openingDateTime}
        placeholderText="JJ/MM/AAAA"
        selected={field.value ?? new Date()}
      />

      {meta.touched && !!meta.error && <FieldError>{meta.error}</FieldError>}
    </div>
  )
}

export default DatePicker
