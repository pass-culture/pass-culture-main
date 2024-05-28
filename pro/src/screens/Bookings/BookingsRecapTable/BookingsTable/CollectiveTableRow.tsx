import cn from 'classnames'
import { useEffect, useRef, useState } from 'react'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { CollectiveBookingResponseModel } from 'apiClient/v1'
import useAnalytics from 'app/App/analytics/firebase'
import { GET_COLLECTIVE_BOOKING_BY_ID_QUERY_KEY } from 'config/swrQueryKeys'
import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import Spinner from 'ui-kit/Spinner/Spinner'
import { doesUserPreferReducedMotion } from 'utils/windowMatchMedia'

import styles from './BookingsTable.module.scss'
import { BookingIdCell } from './Cells/BookingIdCell'
import { BookingOfferCell } from './Cells/BookingOfferCell'
import { CollectiveBookingStatusCell } from './Cells/CollectiveBookingStatusCell'
import { DetailsButtonCell } from './Cells/DetailsButtonCell'
import { InstitutionCell } from './Cells/InstitutionCell'
import { NumberOfTicketsAndPriceCell } from './Cells/NumberOfTicketsAndPriceCell'
import { CollectiveBookingDetails } from './CollectiveBookingDetails'

export interface CollectiveTableRowProps {
  booking: CollectiveBookingResponseModel
  defaultOpenedBookingId: string
}

export const CollectiveTableRow = ({
  booking,
  defaultOpenedBookingId,
}: CollectiveTableRowProps) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const { logEvent } = useAnalytics()

  const detailsRef = useRef<HTMLTableRowElement | null>(null)

  const bookingDetailsQuery = useSWR(
    isExpanded
      ? [GET_COLLECTIVE_BOOKING_BY_ID_QUERY_KEY, Number(booking.bookingId)]
      : null,
    ([, bookingIdParam]) => api.getCollectiveBookingById(bookingIdParam)
  )

  const onRowClick = () => {
    logEvent(CollectiveBookingsEvents.CLICKED_EXPAND_COLLECTIVE_BOOKING_DETAILS)
    setIsExpanded((previousState) => !previousState)
  }

  // We expand row if bookingId match the one in the context
  useEffect(() => {
    if (defaultOpenedBookingId === booking.bookingId) {
      setIsExpanded(true)
      setTimeout(
        () =>
          detailsRef.current?.scrollIntoView({
            behavior: doesUserPreferReducedMotion() ? 'auto' : 'smooth',
          }),
        100
      )
    }
  }, [booking, defaultOpenedBookingId])

  return (
    <>
      <tr className={styles['table-row']} onClick={onRowClick}>
        <td className={cn(styles['table-cell'], styles['column-booking-id'])}>
          <BookingIdCell id={booking.bookingId} />
        </td>

        <td
          className={cn(
            styles['table-cell'],
            styles['column-collective-offer-name']
          )}
        >
          <BookingOfferCell booking={booking} />
        </td>

        <td className={cn(styles['table-cell'], styles['column-institution'])}>
          <InstitutionCell institution={booking.institution} />
        </td>

        <td
          className={cn(styles['table-cell'], styles['column-price-and-price'])}
        >
          <NumberOfTicketsAndPriceCell booking={booking} />
        </td>

        <td
          className={cn(styles['table-cell'], styles['column-booking-status'])}
        >
          <CollectiveBookingStatusCell booking={booking} />
        </td>

        <td className={cn(styles['table-cell'])}>
          <DetailsButtonCell isExpanded={isExpanded} />
        </td>
      </tr>

      {isExpanded ? (
        <tr className={styles['details-container']} ref={detailsRef}>
          {bookingDetailsQuery.isLoading || !bookingDetailsQuery.data ? (
            <td className={styles['loader']}>
              <Spinner />
            </td>
          ) : (
            <td className={styles['details-content']} id={booking.bookingId}>
              <CollectiveBookingDetails
                bookingDetails={bookingDetailsQuery.data}
                bookingRecap={booking}
              />
            </td>
          )}
        </tr>
      ) : null}
    </>
  )
}
