import cn from 'classnames'
import { format } from 'date-fns-tz'
import React from 'react'

import {
  BookingRecapResponseBookingStatusHistoryModel,
  BookingStatusHistoryResponseModel,
} from 'apiClient/v1'
import { toDateStrippedOfTimezone } from 'utils/date'

import { getBookingStatusDisplayInformations } from '../../utils/bookingStatusConverter'

import styles from './BookingStatusCellHistory.module.scss'

const computeDateForStatus = (
  item:
    | BookingRecapResponseBookingStatusHistoryModel
    | BookingStatusHistoryResponseModel,
  dateFormat: string
) => (item.date ? format(toDateStrippedOfTimezone(item.date), dateFormat) : '-')

export interface BookingStatusCellHistoryProps {
  bookingStatusHistory:
    | BookingRecapResponseBookingStatusHistoryModel[]
    | BookingStatusHistoryResponseModel[]
}

export const BookingStatusCellHistory = ({
  bookingStatusHistory,
}: BookingStatusCellHistoryProps) => {
  const bookingsStatusHistoryItems = bookingStatusHistory.map((item) => {
    const displayInfoFromStatus = getBookingStatusDisplayInformations(
      item.status
    )

    if (!displayInfoFromStatus) {
      return <li />
    }

    return (
      <li key={displayInfoFromStatus.status}>
        <span
          className={cn(
            styles['colored-disc'],
            styles[displayInfoFromStatus.historyClassName]
          )}
        />
        {`${displayInfoFromStatus.label} : ${computeDateForStatus(
          item,
          displayInfoFromStatus.dateFormat
        )}`}
      </li>
    )
  })

  return (
    <div className={styles['booking-status-history']}>
      {bookingsStatusHistoryItems}
    </div>
  )
}
