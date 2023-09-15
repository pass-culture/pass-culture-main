import React, { useEffect, useRef, useState } from 'react'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { CollectiveBookingByIdResponseModel } from 'apiClient/v1/models/CollectiveBookingByIdResponseModel'
import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import Spinner from 'ui-kit/Spinner/Spinner'
import { doesUserPreferReducedMotion } from 'utils/windowMatchMedia'

import styles from './BookingsTable.module.scss'
import {
  BookingIdCell,
  BookingOfferCell,
  InstitutionCell,
  NumberOfTicketsAndPriceCell,
  BookingStatusCell,
  DetailsButtonCell,
} from './Cells'
import CollectiveBookingDetails from './CollectiveBookingDetails'
import getCollectiveBookingAdapter from './getCollectiveBookingAdapter'

export interface CollectiveTableRowProps {
  booking: CollectiveBookingResponseModel
  reloadBookings: () => void
  defaultOpenedBookingId: string
}

export const CollectiveTableRow = ({
  booking,
  reloadBookings,
  defaultOpenedBookingId,
}: CollectiveTableRowProps) => {
  const [bookingDetails, setBookingDetails] =
    useState<CollectiveBookingByIdResponseModel | null>(null)
  const [isExpanded, setIsExpanded] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const { logEvent } = useAnalytics()

  const detailsRef = useRef<HTMLTableRowElement | null>(null)

  useEffect(() => {
    const fetchBookingDetails = async () => {
      setIsLoading(true)
      const bookingResponse = await getCollectiveBookingAdapter(
        Number(booking.bookingId)
      )
      if (bookingResponse.isOk) {
        setBookingDetails(bookingResponse.payload)
      }
      setIsLoading(false)
    }

    if (isExpanded && bookingDetails === null) {
      fetchBookingDetails()
    }
  }, [isExpanded])

  const onRowClick = () => {
    logEvent?.(
      CollectiveBookingsEvents.CLICKED_EXPAND_COLLECTIVE_BOOKING_DETAILS
    )
    setIsExpanded(previousState => !previousState)
  }

  // We expand row if bookingId match the one in the context
  useEffect(() => {
    if (defaultOpenedBookingId == booking.bookingId) {
      setIsExpanded(true)
      setTimeout(
        () =>
          detailsRef?.current?.scrollIntoView({
            behavior: doesUserPreferReducedMotion() ? 'auto' : 'smooth',
          }),
        100
      )
    }
  }, [booking, defaultOpenedBookingId])

  return (
    <>
      <tr className={styles['table-row']} onClick={onRowClick}>
        <td className={styles['column-booking-id']}>
          <BookingIdCell id={booking.bookingId} />
        </td>

        <td className={styles['column-collective-offer-name']}>
          <BookingOfferCell booking={booking} isCollective={true} />
        </td>

        <td className={styles['column-institution']}>
          <InstitutionCell institution={booking.institution} />
        </td>

        <td className={styles['column-price-and-price']}>
          <NumberOfTicketsAndPriceCell booking={booking} />
        </td>

        <td className={styles['column-booking-status']}>
          <BookingStatusCell booking={booking} isCollectiveStatus={true} />
        </td>

        <td>
          <DetailsButtonCell isExpanded={isExpanded} />
        </td>
      </tr>

      {isExpanded && (
        <>
          <tr className={styles['details-container']} ref={detailsRef}>
            {isLoading ? (
              <td className={styles['loader']}>
                <Spinner />
              </td>
            ) : (
              bookingDetails && (
                <td
                  className={styles['details-content']}
                  id={booking.bookingId}
                >
                  <CollectiveBookingDetails
                    bookingDetails={bookingDetails}
                    bookingRecap={booking}
                    reloadBookings={reloadBookings}
                  />
                </td>
              )
            )}
          </tr>
        </>
      )}
    </>
  )
}
