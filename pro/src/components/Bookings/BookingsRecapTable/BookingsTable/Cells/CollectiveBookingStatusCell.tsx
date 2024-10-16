import cn from 'classnames'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { getCollectiveBookingStatusDisplayInformations } from '../../utils/bookingStatusConverter'

import styles from './BookingStatusCell.module.scss'

export type CollectiveBookingStatusCellProps = {
  booking: CollectiveBookingResponseModel
  className?: string
}

export function CollectiveBookingStatusCell({
  booking,
  className,
}: CollectiveBookingStatusCellProps) {
  const lastBookingStatus = booking.bookingStatusHistory.slice(-1)[0].status
  const bookingDisplayInfo =
    getCollectiveBookingStatusDisplayInformations(lastBookingStatus)
  if (!bookingDisplayInfo) {
    return null
  }

  return (
    <div className={cn(className)}>
      <div
        className={cn(
          styles['booking-status-label'],
          bookingDisplayInfo.statusClassName
        )}
      >
        <SvgIcon
          src={bookingDisplayInfo.icon}
          alt=""
          className={styles['booking-status-icon']}
        />
        <span>{bookingDisplayInfo.status.toLowerCase()}</span>
      </div>
    </div>
  )
}
