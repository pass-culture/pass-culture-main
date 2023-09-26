import React, { useEffect, useState } from 'react'

import { BookingRecapResponseModel } from 'apiClient/v1'
import { SummaryLayout } from 'components/SummaryLayout'
import {
  DEFAULT_PRE_FILTERS,
  EMPTY_FILTER_VALUE,
} from 'core/Bookings/constants'
import { getFilteredBookingsRecapAdapter } from 'pages/Bookings/adapters'
import { IndividualBookingsTable } from 'screens/Bookings/BookingsRecapTable/BookingsTable/IndividualBookingsTable'
import { DEFAULT_OMNISEARCH_CRITERIA } from 'screens/Bookings/BookingsRecapTable/Filters'
import filterBookingsRecap from 'screens/Bookings/BookingsRecapTable/utils/filterBookingsRecap'
import Spinner from 'ui-kit/Spinner/Spinner'

export const BookingsSummaryScreen = () => {
  const [bookings, setBookings] = useState<BookingRecapResponseModel[] | null>(
    null
  )
  const [bookingsStatusFilters, setBookingsStatusFilter] = useState<string[]>(
    []
  )

  useEffect(() => {
    const loadBookings = async () => {
      const response = await getFilteredBookingsRecapAdapter({
        ...DEFAULT_PRE_FILTERS,
      })

      if (response.isOk) {
        setBookings(response.payload.bookings)
      }
    }
    loadBookings()
  }, [setBookings])

  const filteredBookings = filterBookingsRecap(bookings ?? [], {
    bookingStatus: bookingsStatusFilters,
    // Improve the filtering of the base bookings page, it is a mess
    // because it mixes backend and frontend filtering in weird ways.
    // Thus I must reuse this function with lots of empty values
    // to filter by booking status
    bookingBeneficiary: EMPTY_FILTER_VALUE,
    bookingToken: EMPTY_FILTER_VALUE,
    offerISBN: EMPTY_FILTER_VALUE,
    offerName: EMPTY_FILTER_VALUE,
    selectedOmniSearchCriteria: DEFAULT_OMNISEARCH_CRITERIA,
    keywords: EMPTY_FILTER_VALUE,
    bookingInstitution: EMPTY_FILTER_VALUE,
    bookingId: EMPTY_FILTER_VALUE,
  })

  return (
    <SummaryLayout.Section title="Réservations">
      {bookings !== null ? (
        <IndividualBookingsTable
          bookings={filteredBookings}
          bookingStatuses={bookingsStatusFilters}
          updateGlobalFilters={({ bookingStatus }) => {
            setBookingsStatusFilter(bookingStatus ?? [])
          }}
        />
      ) : (
        <Spinner />
      )}
    </SummaryLayout.Section>
  )
  return
}
