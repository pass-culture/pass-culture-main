import fr from 'date-fns/locale/fr'
import React from 'react'
import ReactDatePicker, { registerLocale } from 'react-datepicker'
import type { ReactDatePickerProps } from 'react-datepicker'

import { FORMAT_HH_mm } from 'utils/date'

import { BaseInput } from '../shared'

registerLocale('fr', fr)

type Props = Omit<ReactDatePickerProps, 'value'> & {
  value?: Date | null | ''
  hasError?: boolean
  filterVariant?: boolean
}

export const isDateValid = (date?: Date | null | ''): date is Date => {
  return date instanceof Date && !isNaN(date.getTime())
}

export const BaseTimePicker = ({
  hasError,
  filterVariant,
  value,
  ...props
}: Props): JSX.Element => {
  // react-datepicker crashes if the value is not a Date or an InvalidDate
  // (InvalidDate is the result of new Date('stringthebrowsercantparse'))
  const selected = isDateValid(value) ? value : null

  return (
    <ReactDatePicker
      {...props}
      customInput={
        <BaseInput hasError={hasError} filterVariant={filterVariant} />
      }
      dateFormat={FORMAT_HH_mm}
      dropdownMode="scroll"
      locale="fr"
      placeholderText="HH:MM"
      showTimeSelect
      showTimeSelectOnly
      timeCaption="Horaire"
      timeIntervals={15}
      onKeyDown={event => {
        !/[0-9:]|Backspace|Tab/.test(event.key) && event.preventDefault()
      }}
      selected={selected}
    />
  )
}
