import { format } from 'date-fns-tz'
import PropTypes from 'prop-types'
import React from 'react'

import { toDateStrippedOfTimezone } from 'utils/date'

import { getBookingStatusDisplayInformations } from './utils/bookingStatusConverter'

const BookingStatusCellHistory = ({ bookingStatusHistory }) => {
  const bookingsStatusHistoryItems = bookingStatusHistory.map(item => {
    const displayInfoFromStatus = getBookingStatusDisplayInformations(
      item.status
    )
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

  function computeDateForStatus(item, dateFormat) {
    return item.date
      ? format(toDateStrippedOfTimezone(item.date), dateFormat)
      : '-'
  }

  return (
    <div className="booking-status-history">{bookingsStatusHistoryItems}</div>
  )
}

BookingStatusCellHistory.propTypes = {
  bookingStatusHistory: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
}

export default BookingStatusCellHistory
