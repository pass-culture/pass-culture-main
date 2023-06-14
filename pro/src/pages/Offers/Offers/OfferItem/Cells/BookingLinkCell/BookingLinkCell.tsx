import React from 'react'

import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import arrowIcon from 'icons/full-arrow-right.svg'
import ListIconButton from 'ui-kit/ListIconButton/ListIconButton'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
} from 'utils/date'

import styles from '../../OfferItem.module.scss'

interface IBookingLinkCellProps {
  bookingId: string
  bookingStatus: string
  offerEventDate?: Date | null
}

const BookingLinkCell = ({
  bookingId,
  bookingStatus,
  offerEventDate,
}: IBookingLinkCellProps) => {
  if (!offerEventDate) {
    return null
  }
  const { logEvent } = useAnalytics()
  const eventDateFormated = formatBrowserTimezonedDateAsUTC(
    offerEventDate,
    FORMAT_ISO_DATE_ONLY
  )
  const bookingLink = `/reservations/collectives?page=1&offerEventDate=${eventDateFormated}&bookingStatusFilter=booked&offerType=all&offerVenueId=all&bookingId=${bookingId}`
  return (
    <ListIconButton
      className={styles['button']}
      url={bookingLink}
      icon={arrowIcon}
      onClick={() =>
        logEvent?.(CollectiveBookingsEvents.CLICKED_SEE_COLLECTIVE_BOOKING, {
          from: location.pathname,
        })
      }
      hasTooltip
    >
      Voir la {bookingStatus == 'PENDING' ? 'préréservation' : 'réservation'}
    </ListIconButton>
  )
}

export default BookingLinkCell
