import cn from 'classnames'
import { format } from 'date-fns'
import React from 'react'

import { FORMAT_ISO_DATE_ONLY, isDateValid } from 'utils/date'

import { BaseInputProps, BaseInput } from '../shared/BaseInput/BaseInput'

import styles from './BaseDatePicker.module.scss'

type Props = Omit<BaseInputProps, 'value'> & {
  maxDate?: Date
  minDate?: Date
  value: string
}

export const BaseDatePicker = ({
  className,
  maxDate,
  minDate,
  id,
  ...props
}: Props): JSX.Element => {
  const minDateFormatted = isDateValid(minDate)
    ? format(minDate, FORMAT_ISO_DATE_ONLY)
    : undefined
  const maxDateFormatted = isDateValid(maxDate)
    ? format(maxDate, FORMAT_ISO_DATE_ONLY)
    : '2050-01-01'

  return (
    <BaseInput
      placeholder="JJ/MM/AAAA"
      type="date"
      min={minDateFormatted}
      max={maxDateFormatted}
      id={id}
      className={cn(className, styles['date-picker'])}
      {...props}
    />
  )
}
