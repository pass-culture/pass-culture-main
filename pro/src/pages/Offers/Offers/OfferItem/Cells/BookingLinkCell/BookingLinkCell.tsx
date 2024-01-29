import React from 'react'

import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import arrowIcon from 'icons/full-arrow-right.svg'
import ListIconButton from 'ui-kit/ListIconButton/ListIconButton'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
} from 'utils/date'

interface BookingLinkCellProps {
  bookingId: number
  bookingStatus: string
  offerEventDate?: Date | null
}

const BookingLinkCell = ({
  bookingId,
  bookingStatus,
  offerEventDate,
}: BookingLinkCellProps) => {
  const { logEvent } = useAnalytics()
  if (!offerEventDate) {
    return null
  }
  const eventDateFormated = formatBrowserTimezonedDateAsUTC(
    offerEventDate,
    FORMAT_ISO_DATE_ONLY
  )
  const bookingLink = `/reservations/collectives?page=1&offerEventDate=${eventDateFormated}&bookingStatusFilter=booked&offerType=all&offerVenueId=all&bookingId=${bookingId}`
  return (
    <ListIconButton
      url={bookingLink}
      isExternal={false}
      icon={arrowIcon}
      onClick={() =>
        logEvent?.(CollectiveBookingsEvents.CLICKED_SEE_COLLECTIVE_BOOKING, {
          from: location.pathname,
        })
      }
    >
      Voir la {bookingStatus == 'PENDING' ? 'préréservation' : 'réservation'}
    </ListIconButton>
  )
}

export default BookingLinkCell
