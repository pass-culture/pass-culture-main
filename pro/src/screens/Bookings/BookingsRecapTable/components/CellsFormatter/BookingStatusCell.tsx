import cn from 'classnames'
import React from 'react'
import { Row } from 'react-table'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import {
  getBookingStatusDisplayInformations,
  getCollectiveBookingStatusDisplayInformations,
} from '../../utils/bookingStatusConverter'

import styles from './BookingStatusCell.module.scss'
import BookingStatusCellHistory from './BookingStatusCellHistory'

export interface BookingStatusCellProps {
  bookingRecapInfo:
    | Row<BookingRecapResponseModel>
    | Row<CollectiveBookingResponseModel>
  isCollectiveStatus: boolean
}

const BookingStatusCell = ({
  bookingRecapInfo,
  isCollectiveStatus,
}: BookingStatusCellProps) => {
  if (isCollectiveStatus) {
    const lastBookingStatus =
      bookingRecapInfo.original.bookingStatusHistory.slice(-1)[0].status
    const bookingDisplayInfo =
      getCollectiveBookingStatusDisplayInformations(lastBookingStatus)
    if (!bookingDisplayInfo) {
      return null
    }

    return (
      <div
        className={cn(
          styles['booking-status-label'],
          styles['booking-status-wrapper'],
          bookingDisplayInfo?.statusClassName
        )}
      >
        <SvgIcon
          src={bookingDisplayInfo.icon}
          alt=""
          className={styles['booking-status-icon']}
        />
        <span>{bookingDisplayInfo.status.toLowerCase()}</span>
      </div>
    )
  }

  const bookingDisplayInfo = getBookingStatusDisplayInformations(
    bookingRecapInfo.original.bookingStatus
  )
  const offerName = bookingRecapInfo.original.stock.offerName

  const statusName = bookingDisplayInfo?.status.toLowerCase()
  const amount = computeBookingAmount(bookingRecapInfo.original.bookingAmount)
  function computeBookingAmount(amount: number) {
    const FREE_AMOUNT = 'Gratuit'
    const AMOUNT_SUFFIX = '\u00a0€'
    return amount ? `${amount}${AMOUNT_SUFFIX}` : FREE_AMOUNT
  }

  return (
    <div
      className={cn(
        styles['booking-status-label'],
        styles['booking-status-wrapper'],
        bookingDisplayInfo?.statusClassName
      )}
    >
      {bookingDisplayInfo && (
        <SvgIcon
          src={bookingDisplayInfo.icon}
          alt=""
          className={styles['booking-status-icon']}
        />
      )}

      <span>{statusName}</span>
      <div className={styles['bs-tooltip']}>
        <div className={styles['bs-offer-title']}>{offerName}</div>
        <div className={styles['bs-offer-amount']}>
          {`Prix : ${amount.replace('.', ',')}`}
        </div>
        <div className={styles['bs-history-title']}>Historique</div>
        <BookingStatusCellHistory
          bookingStatusHistory={bookingRecapInfo.original.bookingStatusHistory}
        />
      </div>
    </div>
  )
}

export default BookingStatusCell
