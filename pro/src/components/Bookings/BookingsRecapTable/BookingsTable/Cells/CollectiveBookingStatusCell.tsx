import { CollectiveBookingResponseModel } from 'apiClient/v1'
import cn from 'classnames'
import { Tag } from 'design-system/Tag/Tag'

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
      <div className={styles['booking-status-label']}>
        <Tag
          label={bookingDisplayInfo.status.toLowerCase()}
          variant={bookingDisplayInfo.variant}
        />
      </div>
    </div>
  )
}
