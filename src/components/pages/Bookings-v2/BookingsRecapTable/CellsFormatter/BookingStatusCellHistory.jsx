import React from 'react'
import * as PropTypes from 'prop-types'
import moment from 'moment'
import {
  computeHistoryClassName,
  getStatusDateFormat,
  getStatusName,
} from './utils/bookingStatusConverter'

const BookingStatusCellHistory = ({ bookingStatusHistory }) => {
  const bookingsStatusHistoryItems = bookingStatusHistory.map(item => (
    <li key={item.status}>
      <span className={`colored-disc ${computeHistoryClassName(item.status)}`} />
      {`${getStatusName(item.status)} : ${computeDateForStatus(item)}`}
    </li>
  ))

  function computeDateForStatus(item) {
    const dateFormat = getStatusDateFormat(item.status)
    return moment.parseZone(item.date).format(dateFormat)
  }

  return (<div className="booking-status-history">
    {bookingsStatusHistoryItems}
  </div>)
}

BookingStatusCellHistory.propTypes = {
  bookingStatusHistory: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
}

export default BookingStatusCellHistory
