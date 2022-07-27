import fr from 'date-fns/locale/fr'
import { useField } from 'formik'
import React, { createRef } from 'react'
import { default as ReactDatePicker, registerLocale } from 'react-datepicker'

import { BaseInput, FieldLayout } from '../shared'

import { ReactComponent as Calendar } from './assets/calendar.svg'

registerLocale('fr', fr)

interface IDatePickerProps {
  name: string
  className?: string
  disabled?: boolean
  label: string
  maxDateTime?: Date
  minDateTime?: Date
  openingDateTime?: Date
  smallLabel?: boolean
}

const DatePicker = ({
  name,
  maxDateTime,
  minDateTime,
  openingDateTime,
  className,
  disabled,
  label,
  smallLabel,
}: IDatePickerProps): JSX.Element => {
  const [field, meta, helpers] = useField({ name, type: 'date' })
  const ref = createRef<HTMLInputElement>()

  return (
    <FieldLayout
      className={className}
      error={meta.error}
      label={label}
      name={name}
      showError={meta.touched && !!meta.error}
      smallLabel={smallLabel}
    >
      <ReactDatePicker
        {...field}
        customInput={
          <BaseInput
            rightIcon={() => <Calendar />}
            hasError={meta.touched && !!meta.error}
            ref={ref}
          />
        }
        dateFormat="dd/MM/yyyy"
        disabled={disabled}
        dropdownMode="scroll"
        id={name}
        locale="fr"
        maxDate={maxDateTime}
        minDate={minDateTime}
        onChange={date => {
          let newDate = date
          if (
            date &&
            maxDateTime &&
            date.toLocaleDateString() === maxDateTime.toLocaleDateString()
          ) {
            newDate = maxDateTime
          }

          helpers.setTouched(true)
          helpers.setValue(newDate, true)
        }}
        openToDate={field.value ? field.value : openingDateTime}
        placeholderText="JJ/MM/AAAA"
        selected={field.value}
      />
    </FieldLayout>
  )
}

export default DatePicker
