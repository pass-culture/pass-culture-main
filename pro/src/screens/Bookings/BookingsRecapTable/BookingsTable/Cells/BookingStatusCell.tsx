import cn from 'classnames'
import React from 'react'

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
import { BookingStatusCellHistory } from './BookingStatusCellHistory'

export interface BookingStatusCellProps {
  booking: BookingRecapResponseModel | CollectiveBookingResponseModel
  isCollectiveStatus: boolean
}

export const BookingStatusCell = ({
  booking,
  isCollectiveStatus,
}: BookingStatusCellProps) => {
  if (isCollectiveStatus) {
    const lastBookingStatus = booking.bookingStatusHistory.slice(-1)[0].status
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
    booking.bookingStatus
  )
  const offerName = booking.stock.offerName

  const statusName = bookingDisplayInfo?.status.toLowerCase()
  const amount = computeBookingAmount(booking.bookingAmount)
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
          bookingStatusHistory={booking.bookingStatusHistory}
        />
      </div>
    </div>
  )
}
