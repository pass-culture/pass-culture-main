import cn from 'classnames'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { getCollectiveBookingStatusDisplayInformations } from '../../utils/bookingStatusConverter'

import styles from './BookingStatusCell.module.scss'

export type CollectiveBookingStatusCellProps = {
  booking: CollectiveBookingResponseModel
}

export function CollectiveBookingStatusCell({
  booking,
}: CollectiveBookingStatusCellProps) {
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
