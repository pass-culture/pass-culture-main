import React from 'react'
import * as PropTypes from "prop-types"
import { FORMAT_DD_MM_YYYY_HH_mm } from "../../../../../utils/date"
import * as moment from "moment"
import { computeHistoryClassName, computeHistoryTitle } from "./utils/bookingStatusConverter"

const BookingStatusCellHistory = ({bookingStatusHistory}) => {
  const bookingsStatusHistoryItems = bookingStatusHistory.map((item) => (
    <li>
        <span className={computeHistoryClassName(item.status)}>
          {computeHistoryTitle(item.status)} : {parseDate(item.date)}
         </span>
    </li>
  ))

  return (
    <div className="booking-status-history">
      <ul>
        {bookingsStatusHistoryItems}
      </ul>
    </div>
  )

  function parseDate(dateToParse) {
    return moment.parseZone(dateToParse).format(FORMAT_DD_MM_YYYY_HH_mm)
  }
}

BookingStatusCellHistory.propTypes = {
  bookingRecapHistory: PropTypes.shape({}).isRequired,
}

export default BookingStatusCellHistory
