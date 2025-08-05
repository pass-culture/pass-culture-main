import cn from 'classnames'
import {
  FORMAT_DD_MM_YYYY,
  FORMAT_HH_mm,
  toDateStrippedOfTimezone,
} from 'commons/utils/date'
import { format } from 'date-fns-tz'

import styles from './BookingDateCell.module.scss'

export interface BookingDateCellProps {
  bookingDateTimeIsoString: string
  className?: string
}

export const BookingDateCell = ({
  bookingDateTimeIsoString,
  className,
}: BookingDateCellProps) => {
  const bookingDate = toDateStrippedOfTimezone(bookingDateTimeIsoString)
  const bookingDateDay = format(bookingDate, FORMAT_DD_MM_YYYY)
  const bookingDateHour = format(bookingDate, FORMAT_HH_mm)

  return (
    <div className={cn(className)}>
      <div>{bookingDateDay}</div>
      <div className={styles['booking-date-subtitle']}>{bookingDateHour}</div>
    </div>
  )
}
