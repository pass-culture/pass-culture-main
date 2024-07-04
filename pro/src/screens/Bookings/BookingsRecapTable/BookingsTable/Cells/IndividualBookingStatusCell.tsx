import cn from 'classnames'

import { BookingRecapResponseModel } from 'apiClient/v1'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { useTooltipProps } from 'ui-kit/Tooltip/useTooltipProps'
import { formatPrice } from 'utils/formatPrice'

import { getBookingStatusDisplayInformations } from '../../utils/bookingStatusConverter'

import styles from './BookingStatusCell.module.scss'
import { BookingStatusCellHistory } from './BookingStatusCellHistory'

export type IndividualBookingStatusCellProps = {
  booking: BookingRecapResponseModel
  className?: string
}

export const IndividualBookingStatusCell = ({
  booking,
  className,
}: IndividualBookingStatusCellProps) => {
  const { isTooltipHidden, ...tooltipProps } = useTooltipProps({})
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
    <div className={cn(className)}>
      <button
        type="button"
        {...tooltipProps}
        className={cn(
          styles['booking-status-label'],
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
        {!isTooltipHidden && (
          <div className={styles['bs-tooltip']}>
            <div className={styles['bs-offer-title']}>{offerName}</div>
            <div
              className={styles['bs-offer-amount']}
            >{`Prix : ${amount}`}</div>
            <div className={styles['bs-history-title']}>Historique</div>
            <BookingStatusCellHistory
              bookingStatusHistory={booking.bookingStatusHistory}
            />
          </div>
        )}
      </button>
    </div>
  )
}
