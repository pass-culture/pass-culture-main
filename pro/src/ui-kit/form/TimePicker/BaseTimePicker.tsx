import fr from 'date-fns/locale/fr'
import React, { createRef } from 'react'
import ReactDatePicker, { registerLocale } from 'react-datepicker'
import type { ReactDatePickerProps } from 'react-datepicker'

import { FORMAT_HH_mm } from 'utils/date'

import { BaseInput } from '../shared'

registerLocale('fr', fr)

type Props = ReactDatePickerProps & {
  hasError?: boolean
  filterVariant?: boolean
}

export const BaseTimePicker = ({
  hasError,
  filterVariant,
  ...props
}: Props): JSX.Element => {
  const ref = createRef<HTMLInputElement>()

  return (
    <ReactDatePicker
      {...props}
      customInput={
        <BaseInput
          hasError={hasError}
          filterVariant={filterVariant}
          ref={ref}
        />
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
    />
  )
}
