import React from 'react'
import { Row } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import useActiveFeature from 'hooks/useActiveFeature'
import Icon from 'ui-kit/Icon/Icon'
import Tooltip from 'ui-kit/Tooltip'

import {
  getBookingStatusDisplayInformations,
  getCollectiveBookingStatusDisplayInformations,
} from '../../utils/bookingStatusConverter'

import BookingStatusCellHistory from './BookingStatusCellHistory'

const BookingStatusCell = ({
  bookingRecapInfo,
  isCollectiveStatus,
}: {
  bookingRecapInfo:
    | Row<BookingRecapResponseModel>
    | Row<CollectiveBookingResponseModel>
  isCollectiveStatus: boolean
}) => {
  const isImproveCollectiveStatusActive = useActiveFeature(
    'WIP_IMPROVE_COLLECTIVE_STATUS'
  )

  if (isImproveCollectiveStatusActive && isCollectiveStatus) {
    const lastBookingStatus =
      bookingRecapInfo.original.booking_status_history.slice(-1)[0].status
    const bookingDisplayInfo =
      getCollectiveBookingStatusDisplayInformations(lastBookingStatus)
    const tooltipId = `tooltip-${bookingRecapInfo.id}`

    return (
      <Tooltip content={bookingDisplayInfo?.label} id={tooltipId}>
        <div
          className={`booking-status-label booking-status-wrapper ${bookingDisplayInfo?.statusClassName}`}
          aria-describedby={tooltipId}
        >
          <Icon svg={bookingDisplayInfo?.svgIconFilename} />
          <span>{bookingDisplayInfo?.status}</span>
        </div>
      </Tooltip>
    )
  }

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
