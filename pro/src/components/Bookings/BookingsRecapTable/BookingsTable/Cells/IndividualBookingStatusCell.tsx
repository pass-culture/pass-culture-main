import cn from 'classnames'

import { BookingRecapResponseModel } from 'apiClient/v1'
import { formatPrice } from 'commons/utils/formatPrice'
import { Tag } from 'design-system/Tag/Tag'
import { useTooltipProps } from 'ui-kit/Tooltip/useTooltipProps'

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
  const { isTooltipHidden, ...tooltipProps } = useTooltipProps()
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
        className={styles['booking-status-label']}
      >
        <Tag
          label={statusName as string}
          variant={bookingDisplayInfo?.variant}
        />
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
