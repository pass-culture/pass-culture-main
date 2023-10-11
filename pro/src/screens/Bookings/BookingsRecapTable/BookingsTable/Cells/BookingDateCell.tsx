import { format } from 'date-fns-tz'
import React from 'react'

import {
  FORMAT_DD_MM_YYYY,
  FORMAT_HH_mm,
  toDateStrippedOfTimezone,
} from 'utils/date'
import { formatPrice } from 'utils/formatPrice'

import styles from './BookingDateCell.module.scss'

export interface BookingDateCellProps {
  bookingDateTimeIsoString: string
  amount: number
  priceCategoryLabel?: string | null
}

export const BookingDateCell = ({
  bookingDateTimeIsoString,
  amount,
  priceCategoryLabel,
}: BookingDateCellProps) => {
  const bookingDate = toDateStrippedOfTimezone(bookingDateTimeIsoString)
  const bookingDateDay = format(bookingDate, FORMAT_DD_MM_YYYY)
  const bookingDateHour = format(bookingDate, FORMAT_HH_mm)

  return (
    <div>
      <div>{bookingDateDay}</div>
      <div className={styles['booking-date-subtitle']}>{bookingDateHour}</div>
      {priceCategoryLabel && (
        <div className={styles['price-category-label']}>
          {priceCategoryLabel}
        </div>
      )}
      <div className={styles['booking-date-subtitle']}>
        {formatPrice(amount)}
      </div>
    </div>
  )
}
