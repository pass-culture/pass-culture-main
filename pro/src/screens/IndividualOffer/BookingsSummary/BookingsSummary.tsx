import format from 'date-fns/format'
import React, { useEffect, useState } from 'react'

import { BookingRecapResponseModel } from 'apiClient/v1'
import { SummaryLayout } from 'components/SummaryLayout'
import {
  DEFAULT_PRE_FILTERS,
  EMPTY_FILTER_VALUE,
} from 'core/Bookings/constants'
import { IndividualOffer } from 'core/Offers/types'
import strokeBookingHold from 'icons/stroke-booking-hold.svg'
import { getFilteredBookingsRecapAdapter } from 'pages/Bookings/adapters'
import { IndividualBookingsTable } from 'screens/Bookings/BookingsRecapTable/BookingsTable/IndividualBookingsTable'
import { DEFAULT_OMNISEARCH_CRITERIA } from 'screens/Bookings/BookingsRecapTable/Filters'
import filterBookingsRecap from 'screens/Bookings/BookingsRecapTable/utils/filterBookingsRecap'
import Spinner from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { FORMAT_ISO_DATE_ONLY } from 'utils/date'
import { pluralize } from 'utils/pluralize'

import styles from './BookingsSummary.module.scss'

interface BookingsSummaryScreenProps {
  offer: IndividualOffer
}

export const BookingsSummaryScreen = ({
  offer,
}: BookingsSummaryScreenProps) => {
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
        offerId: String(offer.id),
        bookingBeginningDate: '2015-01-01',
        bookingEndingDate: format(new Date(), FORMAT_ISO_DATE_ONLY),
      })

      if (response.isOk) {
        setBookings(response.payload.bookings)
      }
    }
    void loadBookings()
  }, [setBookings])

  if (bookings?.length === 0) {
    return (
      <div className={styles['no-data']}>
        <SvgIcon
          className={styles['no-data-icon']}
          src={strokeBookingHold}
          alt=""
          width="128"
          viewBox="0 0 200 156"
        />

        <div>Vous n’avez pas encore de réservations</div>
      </div>
    )
  }

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
        <>
          <div>{pluralize(filteredBookings.length, 'réservation')}</div>
          <IndividualBookingsTable
            bookings={filteredBookings}
            bookingStatuses={bookingsStatusFilters}
            updateGlobalFilters={({ bookingStatus }) => {
              setBookingsStatusFilter(bookingStatus ?? [])
            }}
            resetFilters={() => setBookingsStatusFilter([])}
          />
        </>
      ) : (
        <Spinner />
      )}
    </SummaryLayout.Section>
  )
}
