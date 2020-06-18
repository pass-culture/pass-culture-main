import React from 'react'
import * as PropTypes from 'prop-types'
import { FORMAT_DD_MM_YYYY_HH_mm } from '../../../../../utils/date'
import moment from 'moment'
import { computeHistoryClassName, computeHistoryTitle } from './utils/bookingStatusConverter'

const BookingStatusCellHistory = ({ bookingStatusHistory }) => {
  const bookingsStatusHistoryItems = bookingStatusHistory.map(item => (
    <li key={item.status}>
      <span className={computeHistoryClassName(item.status)}>
        {`${computeHistoryTitle(item.status)} : ${parseDate(item.date)}`}
      </span>
    </li>
  ))

  function parseDate(dateToParse) {
    return moment.parseZone(dateToParse).format(FORMAT_DD_MM_YYYY_HH_mm)
  }

  return (
    <div className="booking-status-history">
      <ul>
        {bookingsStatusHistoryItems}
      </ul>
    </div>
  )
}

BookingStatusCellHistory.propTypes = {
  bookingStatusHistory: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
}

export default BookingStatusCellHistory
