import cn from 'classnames'
import { format } from 'date-fns'
import { type ForwardedRef, forwardRef, useId } from 'react'

import {
  FORMAT_DD_MM_YYYY,
  FORMAT_ISO_DATE_ONLY,
  isDateValid,
} from '@/commons/utils/date'

import styles from './BaseDatePicker.module.scss'

type Props = Omit<
  React.InputHTMLAttributes<HTMLInputElement>,
  'value' | 'placeholder'
> & {
  maxDate?: Date
  minDate?: Date
  value?: string
  hasError?: boolean
}

export const BaseDatePicker = forwardRef(
  (
    {
      className,
      maxDate,
      minDate,
      id,
      hasError,
      'aria-describedby': ariaDescribedBy,
      ...props
    }: Props,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const minDateFormatted = isDateValid(minDate)
      ? format(minDate, FORMAT_ISO_DATE_ONLY)
      : undefined
    const maxDateFormatted = isDateValid(maxDate)
      ? format(maxDate, FORMAT_ISO_DATE_ONLY)
      : '2050-01-01'

    const valueDescriptionId = useId()
    // Native date inputs don't reliably announce their current value before the
    // browser's own "change date" hint, so expose it as a description instead.
    const formattedValue = isDateValid(props.value)
      ? format(new Date(props.value), FORMAT_DD_MM_YYYY)
      : 'Aucune date'

    return (
      <>
        <p
          id={valueDescriptionId}
          aria-hidden="true"
          className={styles['visually-hidden']}
        >
          {formattedValue}
        </p>
        <input
          type="date"
          min={minDateFormatted}
          max={maxDateFormatted}
          id={id}
          ref={ref}
          aria-describedby={
            cn(formattedValue && valueDescriptionId, ariaDescribedBy) ||
            undefined
          }
          className={cn(className, styles['date-picker'], {
            [styles['has-error']]: hasError,
          })}
          {...props}
        />
      </>
    )
  }
)

BaseDatePicker.displayName = 'BaseDatePicker'
