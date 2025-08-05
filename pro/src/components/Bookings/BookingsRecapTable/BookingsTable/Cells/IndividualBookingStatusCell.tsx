import { BookingRecapResponseModel } from 'apiClient/v1'
import cn from 'classnames'
import { Tag } from 'design-system/Tag/Tag'

import { getBookingStatusDisplayInformations } from '../../utils/bookingStatusConverter'

import styles from './BookingStatusCell.module.scss'

export type IndividualBookingStatusCellProps = {
  booking: BookingRecapResponseModel
  className?: string
}

export const IndividualBookingStatusCell = ({
  booking,
  className,
}: IndividualBookingStatusCellProps) => {
  const bookingDisplayInfo = getBookingStatusDisplayInformations(
    booking.bookingStatus
  )
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
