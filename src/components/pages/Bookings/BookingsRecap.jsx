import * as PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState, useMemo } from 'react'

import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import * as pcapi from 'repository/pcapi/pcapi'

import BookingsRecapTable from './BookingsRecapTable/BookingsRecapTable'
import ChoosePreFiltersMessage from './ChoosePreFiltersMessage/ChoosePreFiltersMessage'
import NoBookingsForPreFiltersMessage from './NoBookingsForPreFiltersMessage/NoBookingsForPreFiltersMessage'
import { DEFAULT_PRE_FILTERS } from './PreFilters/_constants'
import PreFilters from './PreFilters/PreFilters'

const MAX_LOADED_PAGES = 5

const BookingsRecap = ({ location, showInformationNotification }) => {
  const [appliedPreFilters, setAppliedPreFilters] = useState({
    bookingBeginningDate: DEFAULT_PRE_FILTERS.bookingBeginningDate,
    bookingEndingDate: DEFAULT_PRE_FILTERS.bookingEndingDate,
    offerEventDate: DEFAULT_PRE_FILTERS.offerEventDate,
    offerVenueId: location.state?.venueId || DEFAULT_PRE_FILTERS.offerVenueId,
  })
  const [bookingsRecap, setBookingsRecap] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [wereBookingsRequested, setWereBookingsRequested] = useState(false)

  const loadBookingsRecap = useCallback(
    async preFilters => {
      setIsLoading(true)
      setBookingsRecap([])
      setWereBookingsRequested(true)
      setAppliedPreFilters({ ...preFilters })

      const bookingsFilters = {
        page: 1,
        venueId: preFilters.offerVenueId,
        eventDate: preFilters.offerEventDate,
        bookingPeriodBeginningDate: preFilters.bookingBeginningDate,
        bookingPeriodEndingDate: preFilters.bookingEndingDate,
      }

      const { pages, bookings_recap: bookingsRecap } = await pcapi
        .loadFilteredBookingsRecap({ ...bookingsFilters })
        .then(response => response)
        .catch(() => ({
          page: 0,
          pages: 0,
          total: 0,
          bookings_recap: [],
        }))
      setBookingsRecap(bookingsRecap)

      while (bookingsFilters.page < Math.min(pages, MAX_LOADED_PAGES)) {
        bookingsFilters.page += 1
        await pcapi
          .loadFilteredBookingsRecap({ ...bookingsFilters })
          .then(({ bookings_recap }) =>
            setBookingsRecap(currentBookingsRecap =>
              [...currentBookingsRecap].concat(bookings_recap)
            )
          )
      }

      setIsLoading(false)
      if (bookingsFilters.page === MAX_LOADED_PAGES && bookingsFilters.page < pages) {
        showInformationNotification()
      }
    },
    [showInformationNotification]
  )

  useEffect(() => {
    if (location.state?.statuses.length > 0) {
      loadBookingsRecap({
        bookingBeginningDate: DEFAULT_PRE_FILTERS.bookingBeginningDate,
        bookingEndingDate: DEFAULT_PRE_FILTERS.bookingEndingDate,
        offerEventDate: DEFAULT_PRE_FILTERS.offerEventDate,
        offerVenueId: location.state?.venueId || DEFAULT_PRE_FILTERS.offerVenueId,
      })
    }
  }, [location.state, loadBookingsRecap])

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

  return (
    <div className="bookings-page">
      <PageTitle title="Vos réservations" />
      <Titles title="Réservations" />
      <h2 className="br-title">
        Affichage des réservations
      </h2>
      {werePreFiltersCustomized && (
        <button
          className="tertiary-button reset-filters-link"
          onClick={resetPreFilters}
          type="button"
        >
          Réinitialiser les filtres
        </button>
      )}
      <PreFilters
        appliedPreFilters={appliedPreFilters}
        applyPreFilters={loadBookingsRecap}
        hasResult={bookingsRecap.length > 0}
        isLoading={isLoading}
        wereBookingsRequested={wereBookingsRequested}
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
    </div>
  )
}

BookingsRecap.propTypes = {
  location: PropTypes.shape({
    state: PropTypes.shape({
      venueId: PropTypes.string,
      statuses: PropTypes.arrayOf(PropTypes.string),
    }),
  }).isRequired,
  showInformationNotification: PropTypes.func.isRequired,
}

export default BookingsRecap
