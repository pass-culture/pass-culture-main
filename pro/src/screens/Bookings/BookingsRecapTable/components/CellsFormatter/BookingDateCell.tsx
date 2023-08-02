import { format } from 'date-fns-tz'
import React from 'react'

import {
  FORMAT_DD_MM_YYYY,
  FORMAT_HH_mm,
  toDateStrippedOfTimezone,
} from 'utils/date'

import styles from './BookingDateCell.module.scss'

export interface BookingDateCellProps {
  bookingDateTimeIsoString: string
}

const BookingDateCell = ({
  bookingDateTimeIsoString,
}: BookingDateCellProps) => {
  const bookingDate = toDateStrippedOfTimezone(bookingDateTimeIsoString)
  const bookingDateDay = format(bookingDate, FORMAT_DD_MM_YYYY)
  const bookingDateHour = format(bookingDate, FORMAT_HH_mm)

  return (
    <div>
      <span>{bookingDateDay}</span>
      <br />
      <span className={styles['booking-date-subtitle']}>{bookingDateHour}</span>
    </div>
  )
}

export default BookingDateCell
