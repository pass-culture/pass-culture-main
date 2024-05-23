import { CollectiveBookingStatus } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import nextIcon from 'icons/full-next.svg'
import { ListIconButton } from 'ui-kit/ListIconButton/ListIconButton'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
  isDateValid,
} from 'utils/date'

interface BookingLinkCellProps {
  bookingId: number
  bookingStatus: string
  offerEventDate?: string | null
}

export const BookingLinkCell = ({
  bookingId,
  bookingStatus,
  offerEventDate,
}: BookingLinkCellProps) => {
  const { logEvent } = useAnalytics()

  if (!isDateValid(offerEventDate)) {
    return null
  }

  const eventDateFormated = formatBrowserTimezonedDateAsUTC(
    new Date(offerEventDate),
    FORMAT_ISO_DATE_ONLY
  )
  const bookingLink = `/reservations/collectives?page=1&offerEventDate=${eventDateFormated}&bookingStatusFilter=booked&offerType=all&offerVenueId=all&bookingId=${bookingId}`

  return (
    <ListIconButton
      url={bookingLink}
      isExternal={false}
      icon={nextIcon}
      onClick={() =>
        logEvent(CollectiveBookingsEvents.CLICKED_SEE_COLLECTIVE_BOOKING, {
          from: location.pathname,
        })
      }
    >
      Voir la{' '}
      {bookingStatus === CollectiveBookingStatus.PENDING
        ? 'préréservation'
        : 'réservation'}
    </ListIconButton>
  )
}
