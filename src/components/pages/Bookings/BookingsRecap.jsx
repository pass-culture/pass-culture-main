import * as PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState, useMemo } from 'react'

import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import * as pcapi from 'repository/pcapi/pcapi'

import BookingsRecapTable from './BookingsRecapTable/BookingsRecapTable'
import BookingsRecapTableLegacy from './BookingsRecapTableLegacy/BookingsRecapTableLegacy' /* eslint-disable-line react/jsx-pascal-case */
import ChoosePreFiltersMessage from './ChoosePreFiltersMessage/ChoosePreFiltersMessage'
import NoBookingsForPreFiltersMessage from './NoBookingsForPreFiltersMessage/NoBookingsForPreFiltersMessage'
import NoBookingsMessage from './NoBookingsMessage/NoBookingsMessage'
import { DEFAULT_PRE_FILTERS } from './PreFilters/_constants'
import PreFilters from './PreFilters/PreFilters'

const MAX_LOADED_PAGES = 5

const BookingsRecap = ({
  arePreFiltersEnabled,
  isUserAdmin,
  location,
  showWarningNotification,
}) => {
  const [appliedPreFilters, setAppliedPreFilters] = useState({
    bookingBeginningDate: DEFAULT_PRE_FILTERS.bookingBeginningDate,
    bookingEndingDate: DEFAULT_PRE_FILTERS.bookingEndingDate,
    offerEventDate: DEFAULT_PRE_FILTERS.offerEventDate,
    offerVenueId: location.state?.venueId || DEFAULT_PRE_FILTERS.offerVenueId,
  })
  const [bookingsRecap, setBookingsRecap] = useState([])
  const [isLoading, setIsLoading] = useState(arePreFiltersEnabled ? false : true)
  const [wereBookingsRequested, setWereBookingsRequested] = useState(false)

  const loadBookingsRecap = useCallback(
    async preFilters => {
      setIsLoading(true)
      setBookingsRecap([])
      setWereBookingsRequested(true)
      setAppliedPreFilters({ ...preFilters })

      // TODO(07/06/2021): To remove when 'ENABLE_BOOKINGS_PAGE_FILTERS_FIRST' feature flip has been removed
      let bookingsFilters = {}
      if (preFilters) {
        bookingsFilters = {
          venueId: preFilters.offerVenueId,
          eventDate: preFilters.offerEventDate,
        }
      }

      let currentPage = 1
      const { pages, bookings_recap: bookingsRecap } = await pcapi.loadFilteredBookingsRecap({
        page: currentPage,
        ...bookingsFilters,
      })
      setBookingsRecap(bookingsRecap)

      while (currentPage < Math.min(pages, MAX_LOADED_PAGES)) {
        currentPage += 1
        await pcapi
          .loadFilteredBookingsRecap({ page: currentPage, ...bookingsFilters })
          .then(({ bookings_recap }) =>
            setBookingsRecap(currentBookingsRecap =>
              [...currentBookingsRecap].concat(bookings_recap)
            )
          )
      }

      setIsLoading(false)
      if (currentPage === MAX_LOADED_PAGES && currentPage < pages) {
        showWarningNotification()
      }
    },
    [showWarningNotification]
  )

  useEffect(() => {
    if (!arePreFiltersEnabled) {
      loadBookingsRecap()
    }
  }, [arePreFiltersEnabled, loadBookingsRecap])

  const werePreFiltersCustomized = useMemo(() => {
    return (
      appliedPreFilters.offerVenueId !== DEFAULT_PRE_FILTERS.offerVenueId ||
      appliedPreFilters.bookingBeginningDate !== DEFAULT_PRE_FILTERS.bookingBeginningDate ||
      appliedPreFilters.bookingEndingDate !== DEFAULT_PRE_FILTERS.bookingEndingDate ||
      appliedPreFilters.offerEventDate !== DEFAULT_PRE_FILTERS.offerEventDate
    )
  }, [
    appliedPreFilters.bookingBeginningDate,
    appliedPreFilters.bookingEndingDate,
    appliedPreFilters.offerEventDate,
    appliedPreFilters.offerVenueId,
  ])

  const resetPreFilters = useCallback(() => {
    setWereBookingsRequested(false)
    setAppliedPreFilters({ ...DEFAULT_PRE_FILTERS })
  }, [])

  if (isUserAdmin) return <NoBookingsMessage />

  return (
    <div className="bookings-page">
      <PageTitle title="Vos réservations" />
      <Titles title="Réservations" />
      <h2 className="br-title">
        {'Affichage des réservations'}
      </h2>
      {werePreFiltersCustomized && (
        <button
          className="tertiary-button reset-filters-link"
          onClick={resetPreFilters}
          type="button"
        >
          {'Réinitialiser les filtres'}
        </button>
      )}
      {arePreFiltersEnabled ? (
        <>
          <PreFilters
            appliedPreFilters={appliedPreFilters}
            applyPreFilters={loadBookingsRecap}
            isLoading={isLoading}
          />
          {wereBookingsRequested ? (
            bookingsRecap.length > 0 ? (
              <BookingsRecapTable
                bookingsRecap={bookingsRecap}
                isLoading={isLoading}
                locationState={location.state}
              />
            ) : isLoading ? (
              <Spinner />
            ) : (
              <NoBookingsForPreFiltersMessage resetPreFilters={resetPreFilters} />
            )
          ) : (
            <ChoosePreFiltersMessage />
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
  isUserAdmin: PropTypes.bool.isRequired,
  location: PropTypes.shape({
    state: PropTypes.shape({
      venueId: PropTypes.string,
      statuses: PropTypes.arrayOf(PropTypes.string),
    }),
  }).isRequired,
  showWarningNotification: PropTypes.func.isRequired,
}

export default BookingsRecap
