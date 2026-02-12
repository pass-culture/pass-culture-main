import { format } from 'date-fns-tz'

import {
  FORMAT_DD_MM_YYYY,
  FORMAT_HH_mm,
  toDateStrippedOfTimezone,
} from '@/commons/utils/date'

import styles from './BookingDateCell.module.scss'

export interface BookingDateCellProps {
  bookingDateTime: string
}

export const BookingDateCell = ({ bookingDateTime }: BookingDateCellProps) => {
  const bookingDate = toDateStrippedOfTimezone(bookingDateTime)
  const bookingDateDay = format(bookingDate, FORMAT_DD_MM_YYYY)
  const bookingDateHour = format(bookingDate, FORMAT_HH_mm)

  return (
    <div>
      <div>{bookingDateDay}</div>
      <div className={styles['booking-date-subtitle']}>{bookingDateHour}</div>
    </div>
  )
}
