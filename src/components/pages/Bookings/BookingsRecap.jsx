/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import * as PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState, useMemo } from 'react'

import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import * as pcapi from 'repository/pcapi/pcapi'
import { API_URL } from 'utils/config'

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

      let filteredBookingsResponse
      try  {
        filteredBookingsResponse = await pcapi.loadFilteredBookingsRecap(bookingsFilters)
      } catch {
        filteredBookingsResponse = {
          page: 0,
          pages: 0,
          total: 0,
          bookings_recap: [],
        }
      }
      const { pages, bookings_recap: bookingsRecap } = filteredBookingsResponse
      setBookingsRecap(bookingsRecap)

      let currentPage = bookingsFilters.page
      while (currentPage < Math.min(pages, MAX_LOADED_PAGES)) {
        currentPage += 1
        const nextPageFilters = {
          ...bookingsFilters,
          page: currentPage,
        }
        const response = await pcapi.loadFilteredBookingsRecap(nextPageFilters)
        setBookingsRecap(currentBookingsRecap =>
          [...currentBookingsRecap].concat(response.bookings_recap)
        )
      }

      setIsTableLoading(false)
      if (currentPage === MAX_LOADED_PAGES && currentPage < pages) {
        showInformationNotification()
      }
    },
    [showInformationNotification]
  )

  const downloadBookingsCSV = useCallback(async filters => {
    const queryParams = pcapi.buildBookingsRecapQuery(filters)
    const result = await fetch(`${API_URL}/bookings/csv?${queryParams}`, { credentials: 'include' })

    if (result.status === 200) {
      const text = await result.text()
      const fakeLink = document.createElement('a')
      const blob = new Blob([text], { type: "text/csv" })
      const date = new Date().toISOString()
      fakeLink.href = URL.createObjectURL(blob)
      fakeLink.setAttribute('download', `reservations_pass_culture-${date}.csv`)
      document.body.appendChild(fakeLink)
      fakeLink.click()
      document.body.removeChild(fakeLink)
    }
  }, [])

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
        downloadBookingsCSV={downloadBookingsCSV}
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
