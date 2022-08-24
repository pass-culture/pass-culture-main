import React from 'react'
import { Row } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import Icon from 'components/layout/Icon'

import { getBookingStatusDisplayInformations } from '../../utils/bookingStatusConverter'

import BookingStatusCellHistory from './BookingStatusCellHistory'

const BookingStatusCell = ({
  bookingRecapInfo,
}: {
  bookingRecapInfo:
    | Row<BookingRecapResponseModel>
    | Row<CollectiveBookingResponseModel>
}) => {
  const bookingDisplayInfo = getBookingStatusDisplayInformations(
    bookingRecapInfo.original.booking_status
  )
  const offerName = bookingRecapInfo.original.stock.offer_name

  const statusClassName = bookingDisplayInfo?.statusClassName
  const statusName = bookingDisplayInfo?.status
  const amount = computeBookingAmount(bookingRecapInfo.original.booking_amount)
  const icon = bookingDisplayInfo?.svgIconFilename

  function computeBookingAmount(amount: number) {
    const FREE_AMOUNT = 'Gratuit'
    const AMOUNT_SUFFIX = '\u00a0€'
    return amount ? `${amount}${AMOUNT_SUFFIX}` : FREE_AMOUNT
  }

  return (
    <div
      className={`booking-status-label booking-status-wrapper ${statusClassName}`}
    >
      <Icon svg={icon} />
      <span>{statusName}</span>
      <div className="bs-tooltip">
        <div className="bs-offer-title">{offerName}</div>
        <div className="bs-offer-amount">
          {`Prix : ${amount.replace('.', ',')}`}
        </div>
        <div className="bs-history-title">Historique</div>
        <BookingStatusCellHistory
          bookingStatusHistory={
            bookingRecapInfo.original.booking_status_history
          }
        />
      </div>
    </div>
  )
}

export default BookingStatusCell
