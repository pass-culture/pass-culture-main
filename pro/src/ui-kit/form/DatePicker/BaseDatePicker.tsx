import fr from 'date-fns/locale/fr'
import React, { createRef } from 'react'
import ReactDatePicker, { registerLocale } from 'react-datepicker'
import type { ReactDatePickerProps } from 'react-datepicker'

import { CalendarIcon } from 'icons'
import { FORMAT_DD_MM_YYYY } from 'utils/date'

import { BaseInput } from '../shared'

registerLocale('fr', fr)

type Props = ReactDatePickerProps & {
  hasError?: boolean
  filterVariant?: boolean
}

export const BaseDatePicker = ({
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
          rightIcon={() => <CalendarIcon />}
          hasError={hasError}
          filterVariant={filterVariant}
          ref={ref}
        />
      }
      dateFormat={FORMAT_DD_MM_YYYY}
      dropdownMode="scroll"
      locale="fr"
      placeholderText="JJ/MM/AAAA"
    />
  )
}
