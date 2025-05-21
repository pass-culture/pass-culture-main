import { format } from 'date-fns-tz'

import {
  BookingRecapResponseBookingStatusHistoryModel,
  BookingStatusHistoryResponseModel,
} from 'apiClient/v1'
import { toDateStrippedOfTimezone } from 'commons/utils/date'

import { getBookingStatusDisplayInformations } from '../../utils/bookingStatusConverter'

import styles from './BookingStatusCellHistory.module.scss'

const computeDateForStatus = (
  item:
    | BookingRecapResponseBookingStatusHistoryModel
    | BookingStatusHistoryResponseModel,
  dateFormat: string
) => (item.date ? format(toDateStrippedOfTimezone(item.date), dateFormat) : '-')

export interface BookingStatusCellHistoryProps {
  index: number
  bookingStatusHistory:
    | BookingRecapResponseBookingStatusHistoryModel[]
    | BookingStatusHistoryResponseModel[]
}

export const BookingStatusCellHistory = ({
  index,
  bookingStatusHistory,
}: BookingStatusCellHistoryProps) => {
  const bookingsStatusHistoryItems = bookingStatusHistory.map((item) => {
    const displayInfoFromStatus = getBookingStatusDisplayInformations(
      item.status
    )

    if (!displayInfoFromStatus || bookingStatusHistory.length < 1) {
      return null
    }

    return (
      <li
        key={displayInfoFromStatus.status}
        className={styles['booking-status-history-list-element']}
      >
        {`${displayInfoFromStatus.label} : ${computeDateForStatus(
          item,
          displayInfoFromStatus.dateFormat
        )}`}
      </li>
    )
  })

  return (
    <>
      <div
        id={`booking-status-history-title-${index}`}
        className={styles['booking-status-history-title']}
      >
        Historique
      </div>
      <ul
        aria-labelledby={`booking-status-history-title-${index}`}
        className={styles['booking-status-history-list']}
      >
        {bookingsStatusHistoryItems}
      </ul>
    </>
  )
}
