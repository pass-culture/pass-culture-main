import fr from 'date-fns/locale/fr'
import { useField } from 'formik'
import React, { createRef } from 'react'
import { default as ReactDatePicker, registerLocale } from 'react-datepicker'

import { FORMAT_DD_MM_YYYY } from 'utils/date'

import { BaseInput, FieldLayout } from '../shared'

import { ReactComponent as Calendar } from './assets/calendar.svg'

registerLocale('fr', fr)

interface IDatePickerProps {
  name: string
  className?: string
  classNameLabel?: string
  classNameFooter?: string
  disabled?: boolean
  label: string
  isLabelHidden?: boolean
  maxDateTime?: Date
  minDateTime?: Date
  openingDateTime?: Date
  smallLabel?: boolean
  isOptional?: boolean
  hideFooter?: boolean
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
}: IDatePickerProps): JSX.Element => {
  const [field, meta, helpers] = useField({ name, type: 'date' })
  const ref = createRef<HTMLInputElement>()
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
      <ReactDatePicker
        {...field}
        customInput={
          <BaseInput
            rightIcon={() => <Calendar />}
            hasError={meta.touched && !!meta.error}
            ref={ref}
          />
        }
        dateFormat={FORMAT_DD_MM_YYYY}
        disabled={disabled}
        dropdownMode="scroll"
        id={name}
        locale="fr"
        maxDate={maxDateTime}
        minDate={minDateTime}
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
        openToDate={field.value ? field.value : openingDateTime}
        placeholderText="JJ/MM/AAAA"
        selected={field.value}
      />
    </FieldLayout>
  )
}

export default DatePicker
