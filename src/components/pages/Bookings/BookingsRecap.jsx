import * as PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'

import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import * as pcapi from 'repository/pcapi/pcapi'

import BookingsRecapTable from './BookingsRecapTable/BookingsRecapTable'
import BookingsRecapTableLegacy from './BookingsRecapTableLegacy/BookingsRecapTableLegacy' /* eslint-disable-line react/jsx-pascal-case */
import NoBookingsMessage from './NoBookingsMessage/NoBookingsMessage'
import { ALL_VENUES, EMPTY_FILTER_VALUE } from './PreFilters/_constants'
import PreFilters from './PreFilters/PreFilters'

const MAX_LOADED_PAGES = 5

const BookingsRecap = ({ arePreFiltersEnabled, location, showWarningNotification }) => {
  const [bookingsRecap, setBookingsRecap] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [preFilters, setPreFilters] = useState({
    bookingBeginningDate: EMPTY_FILTER_VALUE,
    bookingEndingDate: EMPTY_FILTER_VALUE,
    offerDate: EMPTY_FILTER_VALUE,
    offerVenueId: ALL_VENUES,
  })

  useEffect(() => {
    async function loadBookingsRecap() {
      setIsLoading(true)
      setBookingsRecap([])

      let currentPage = 1
      const { pages, bookings_recap: bookingsRecap } = await pcapi.loadFilteredBookingsRecap({page: currentPage,
        venueId: preFilters.offerVenueId,
      })
      setBookingsRecap(bookingsRecap)

      while (currentPage < Math.min(pages, MAX_LOADED_PAGES)) {
        currentPage += 1
        await pcapi.loadFilteredBookingsRecap({page: currentPage,
          venueId: preFilters.offerVenueId,
        }).then(({ bookings_recap }) =>
          setBookingsRecap(currentBookingsRecap => [...currentBookingsRecap].concat(bookings_recap))
        )
      }

      setIsLoading(false)
      if (currentPage === MAX_LOADED_PAGES && currentPage < pages) {
        showWarningNotification()
      }
    }
    loadBookingsRecap()
  }, [preFilters.offerVenueId, showWarningNotification])

  return (
    <div className="bookings-page">
      <PageTitle title="Vos réservations" />
      <Titles title="Réservations" />
      {arePreFiltersEnabled ? (
        <>
          <PreFilters
            applyPreFilters={setPreFilters}
            offerVenueId={location.state?.venueId}
          />
          {bookingsRecap.length > 0 && (
            <BookingsRecapTable
              bookingsRecap={bookingsRecap}
              isLoading={isLoading}
              locationState={location.state}
            />
          )}
        </>
      ) : bookingsRecap.length > 0 ? (
        <BookingsRecapTableLegacy
          bookingsRecap={bookingsRecap}
          isLoading={isLoading}
          locationState={location.state}
        />
      ) : isLoading ? (
        <Spinner />
      ) : (
        <NoBookingsMessage />
      )}
    </div>
  )
}

BookingsRecap.propTypes = {
  arePreFiltersEnabled: PropTypes.bool.isRequired,
  location: PropTypes.shape({
    state: PropTypes.shape({
      venueId: PropTypes.string,
      statuses: PropTypes.arrayOf(PropTypes.string),
    }),
  }).isRequired,
  showWarningNotification: PropTypes.func.isRequired,
}

export default BookingsRecap
