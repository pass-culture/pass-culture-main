import cn from 'classnames'
import { useEffect, useRef, useState } from 'react'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { GET_COLLECTIVE_BOOKING_BY_ID_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { formatPrice } from 'commons/utils/formatPrice'
import { pluralizeString } from 'commons/utils/pluralize'
import { doesUserPreferReducedMotion } from 'commons/utils/windowMatchMedia'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import styles from './BookingsTable.module.scss'
import { BookingOfferCell } from './Cells/BookingOfferCell'
import { CollectiveBookingStatusCell } from './Cells/CollectiveBookingStatusCell'
import { DetailsButtonCell } from './Cells/DetailsButtonCell'
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

  const detailsRef = useRef<HTMLTableRowElement | null>(null)

  const bookingDetailsQuery = useSWR(
    isExpanded
      ? [GET_COLLECTIVE_BOOKING_BY_ID_QUERY_KEY, Number(booking.bookingId)]
      : null,
    ([, bookingIdParam]) => api.getCollectiveBookingById(bookingIdParam)
  )

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

  const institutionName =
    `${booking.institution.institutionType} ${booking.institution.name}`.trim()
  const institutionAddress =
    `${booking.institution.postalCode} ${booking.institution.city}`.trim()
  const numberOfTickets = booking.stock.numberOfTickets

  return (
    <>
      <tr className={styles['table-row']} data-testid="offer-item-row">
        <td
          className={cn(styles['table-cell'], styles['column-booking-id'])}
          data-label="Réservation"
        >
          <div className={styles['cell-item-wrapper']}>{booking.bookingId}</div>
        </td>

        <td
          className={cn(
            styles['table-cell'],
            styles['column-collective-offer-name']
          )}
          data-label="Nom de l’offre"
        >
          <BookingOfferCell
            booking={booking}
            className={styles['cell-item-wrapper']}
          />
        </td>

        <td
          className={cn(styles['table-cell'], styles['column-institution'])}
          data-label="Établissement"
        >
          <div className={styles['cell-item-wrapper']}>
            <div>
              <span data-testid="booking-offer-institution">
                {institutionName}
              </span>
              <br />
            </div>
            <span className={styles['institution-cell-subtitle']}>
              {institutionAddress}
            </span>
          </div>
        </td>

        <td
          className={cn(styles['table-cell'], styles['column-price-and-price'])}
          data-label="Places et prix"
        >
          <div className={styles['cell-item-wrapper']}>
            <div>
              {numberOfTickets} {pluralizeString('place', numberOfTickets)}
            </div>
            <div>
              {formatPrice(booking.bookingAmount, {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
                trailingZeroDisplay: 'stripIfInteger',
              })}
            </div>
          </div>
        </td>

        <td
          className={cn(styles['table-cell'], styles['column-booking-status'])}
          data-label="Statut"
        >
          <CollectiveBookingStatusCell
            booking={booking}
            className={styles['cell-item-wrapper']}
          />
        </td>

        <td className={cn(styles['table-cell'])} data-label="Détails">
          <DetailsButtonCell
            controlledId={`booking-details-${booking.bookingId}`}
            isExpanded={isExpanded}
            className={styles['cell-item-wrapper']}
            onClick={() => {
              setIsExpanded((prev) => !prev)
            }}
          />
        </td>
      </tr>

      {isExpanded ? (
        <tr
          id={`booking-details-${booking.bookingId}`}
          className={styles['details-row']}
          ref={detailsRef}
        >
          {bookingDetailsQuery.isLoading || !bookingDetailsQuery.data ? (
            <td className={styles['loader']} colSpan={6}>
              <Spinner />
            </td>
          ) : (
            <td
              className={styles['details-cell']}
              id={booking.bookingId}
              colSpan={6}
            >
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
