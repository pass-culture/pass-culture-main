import React from 'react'
import PropTypes from 'prop-types'
import moment from 'moment'
import { FORMAT_DD_MM_YYYY_HH_mm } from "../../../../../utils/date"
import {
  computeBookingHistoryClassName,
  computeHistoryDatetypeToStatus,
  computeHistoryTitleFromStatus,
} from "./utils/bookingStatusConverter"

const BookingStatusCellHistory = (historyDate, historyDateType) => {
  const historyDatetypeInfos = computeHistoryDatetypeToStatus(historyDateType)
  const historyDateClassName = computeBookingHistoryClassName(historyDatetypeInfos.status)

  const parsedHistoryDatetypeInfos = moment.parseZone(historyDate)
  const dateToDisplay = parsedHistoryDatetypeInfos.format(FORMAT_DD_MM_YYYY_HH_mm)

  //const historyTitle = computeHistoryTitleFromStatus(historyDatetypeInfos.status)
  const historyTitle = 'Title'

  return (
    <div className="booking-status-history">
      <span className={`booking-status-history ${historyDateClassName}`}>
        {historyTitle} : {dateToDisplay}
      </span>
    </div>
  )
}

BookingStatusCellHistory.propTypes = {
  historyDate: PropTypes.string.isRequired,
  historyDateType: PropTypes.string.isRequired,
}

export default BookingStatusCellHistory
