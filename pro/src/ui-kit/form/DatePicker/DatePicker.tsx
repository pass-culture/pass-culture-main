import fr from 'date-fns/locale/fr'
import { useField } from 'formik'
import React from 'react'
import { registerLocale } from 'react-datepicker'

import { FieldLayout } from '../shared'
import { FieldLayoutBaseProps } from '../shared/FieldLayout/FieldLayout'

import { BaseDatePicker } from './BaseDatePicker'

registerLocale('fr', fr)

export interface DatePickerProps extends FieldLayoutBaseProps {
  disabled?: boolean
  maxDateTime?: Date
  minDateTime?: Date
  openingDateTime?: Date
  hideHiddenFooter?: boolean
  onChange?: (name: string, date: Date | null) => void
}

const DatePicker = ({
  name,
  maxDateTime,
  minDateTime,
  openingDateTime,
  className,
  classNameLabel,
  classNameFooter,
  disabled,
  label,
  isLabelHidden = false,
  smallLabel,
  isOptional = false,
  onChange,
  hideFooter = false,
  hideHiddenFooter = false,
  filterVariant,
}: DatePickerProps): JSX.Element => {
  const [field, meta, helpers] = useField({ name, type: 'date' })
  const showError = meta.touched && !!meta.error

  return (
    <FieldLayout
      className={className}
      classNameLabel={classNameLabel}
      classNameFooter={classNameFooter}
      error={meta.error}
      label={label}
      isLabelHidden={isLabelHidden}
      name={name}
      showError={showError}
      smallLabel={smallLabel}
      isOptional={isOptional}
      hideFooter={hideFooter || (hideHiddenFooter && !showError)}
    >
      <BaseDatePicker
        {...field}
        id={name}
        hasError={meta.touched && !!meta.error}
        filterVariant={filterVariant}
        disabled={disabled}
        maxDate={maxDateTime}
        minDate={minDateTime}
        openToDate={field.value ? field.value : openingDateTime}
        selected={field.value}
        onChange={date => {
          let newDate = date
          /* istanbul ignore next: DEBT, TO FIX */
          if (
            date &&
            maxDateTime &&
            date.toLocaleDateString() === maxDateTime.toLocaleDateString()
          ) {
            newDate = maxDateTime
          }
          onChange && onChange(name, newDate)

          helpers.setTouched(true)
          helpers.setValue(newDate, true)
        }}
      />
    </FieldLayout>
  )
}

export default DatePicker
