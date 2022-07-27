import fr from 'date-fns/locale/fr'
import { useField } from 'formik'
import React, { createRef } from 'react'
import ReactDatePicker, { registerLocale } from 'react-datepicker'

import { BaseInput, FieldLayout } from '../shared'

registerLocale('fr', fr)

interface ITimePickerProps {
  name: string
  className?: string
  disabled?: boolean
  label: string
  dateTime?: Date
  smallLabel?: boolean
}

const TimePicker = ({
  name,
  className,
  disabled,
  label,
  smallLabel,
}: ITimePickerProps): JSX.Element => {
  const [field, meta, helpers] = useField({ name, type: 'text' })
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
          <BaseInput hasError={meta.touched && !!meta.error} ref={ref} />
        }
        dateFormat="HH:mm"
        disabled={disabled}
        dropdownMode="scroll"
        locale="fr"
        onChange={time => {
          helpers.setTouched(true)
          helpers.setValue(time)
        }}
        placeholderText="HH:MM"
        selected={field.value}
        showTimeSelect
        showTimeSelectOnly
        timeCaption="Horaire"
        timeFormat="HH:mm"
        timeIntervals={15}
      />
    </FieldLayout>
  )
}

export default TimePicker
