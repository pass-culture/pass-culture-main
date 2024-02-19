import cn from 'classnames'

import { BookingRecapResponseModel } from 'apiClient/v1'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { formatPrice } from 'utils/formatPrice'

import { getBookingStatusDisplayInformations } from '../../utils/bookingStatusConverter'

import styles from './BookingStatusCell.module.scss'
import { BookingStatusCellHistory } from './BookingStatusCellHistory'

export type IndividualBookingStatusCellProps = {
  booking: BookingRecapResponseModel
}

export const IndividualBookingStatusCell = ({
  booking,
}: IndividualBookingStatusCellProps) => {
  const bookingDisplayInfo = getBookingStatusDisplayInformations(
    booking.bookingStatus
  )
  const offerName = booking.stock.offerName

  const statusName = bookingDisplayInfo?.status.toLowerCase()
  const amount = computeBookingAmount(booking.bookingAmount)
  function computeBookingAmount(amount: number) {
    const FREE_AMOUNT = 'Gratuit'
    return amount ? formatPrice(amount) : FREE_AMOUNT
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
          width="300"
        />
      )}

      <span>{statusName}</span>
      <div className={styles['bs-tooltip']}>
        <div className={styles['bs-offer-title']}>{offerName}</div>
        <div className={styles['bs-offer-amount']}>{`Prix : ${amount}`}</div>
        <div className={styles['bs-history-title']}>Historique</div>
        <BookingStatusCellHistory
          bookingStatusHistory={booking.bookingStatusHistory}
        />
      </div>
    </div>
  )
}
