import cn from 'classnames'
import { format } from 'date-fns'
import { type ForwardedRef, forwardRef } from 'react'

import { FORMAT_ISO_DATE_ONLY, isDateValid } from '@/commons/utils/date'

import { BaseInput, type BaseInputProps } from '../BaseInput/BaseInput'
import styles from './BaseDatePicker.module.scss'

type Props = Omit<BaseInputProps, 'value'> & {
  maxDate?: Date
  minDate?: Date
  value?: string
}

export const BaseDatePicker = forwardRef(
  (
    { className, maxDate, minDate, id, ...props }: Props,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const minDateFormatted = isDateValid(minDate)
      ? format(minDate, FORMAT_ISO_DATE_ONLY)
      : undefined
    const maxDateFormatted = isDateValid(maxDate)
      ? format(maxDate, FORMAT_ISO_DATE_ONLY)
      : '2050-01-01'

    return (
      <BaseInput
        type="date"
        min={minDateFormatted}
        max={maxDateFormatted}
        id={id}
        ref={ref}
        className={cn(className, styles['date-picker'])}
        {...props}
      />
    )
  }
)

BaseDatePicker.displayName = 'BaseDatePicker'
