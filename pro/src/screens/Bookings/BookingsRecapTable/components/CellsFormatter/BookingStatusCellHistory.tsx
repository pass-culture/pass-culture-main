import { format } from 'date-fns-tz'
import React from 'react'

import {
  BookingRecapResponseBookingStatusHistoryModel,
  BookingStatusHistoryResponseModel,
} from 'apiClient/v1'
import { toDateStrippedOfTimezone } from 'utils/date'

import { getBookingStatusDisplayInformations } from '../../utils/bookingStatusConverter'

const BookingStatusCellHistory = ({
  bookingStatusHistory,
}: {
  bookingStatusHistory:
    | BookingRecapResponseBookingStatusHistoryModel[]
    | BookingStatusHistoryResponseModel[]
}) => {
  const bookingsStatusHistoryItems = bookingStatusHistory.map(item => {
    const displayInfoFromStatus = getBookingStatusDisplayInformations(
      item.status
    )

    if (!displayInfoFromStatus) {
      return <li />
    }

    return (
      <li key={displayInfoFromStatus.status}>
        <span
          className={`colored-disc ${displayInfoFromStatus.historyClassName}`}
        />
        {`${displayInfoFromStatus.label} : ${computeDateForStatus(
          item,
          displayInfoFromStatus.dateFormat
        )}`}
      </li>
    )
  })

  function computeDateForStatus(
    item:
      | BookingRecapResponseBookingStatusHistoryModel
      | BookingStatusHistoryResponseModel,
    dateFormat: string
  ) {
    return item.date
      ? format(toDateStrippedOfTimezone(item.date), dateFormat)
      : '-'
  }

  return (
    <div className="booking-status-history">{bookingsStatusHistoryItems}</div>
  )
}

export default BookingStatusCellHistory
