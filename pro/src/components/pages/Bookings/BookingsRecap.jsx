import * as PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState, useMemo } from 'react'

import useActiveFeature from 'components/hooks/useActiveFeature'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import * as pcapi from 'repository/pcapi/pcapi'

import BookingsRecapTable from './BookingsRecapTable/BookingsRecapTable'
import ChoosePreFiltersMessage from './ChoosePreFiltersMessage/ChoosePreFiltersMessage'
import { downloadCSVFile } from './downloadCSVBookings'
import NoBookingsForPreFiltersMessage from './NoBookingsForPreFiltersMessage/NoBookingsForPreFiltersMessage'
import { DEFAULT_PRE_FILTERS } from './PreFilters/_constants'
import PreFilters from './PreFilters/PreFilters'

const MAX_LOADED_PAGES = 5

const BookingsRecap = ({ location, showNotification }) => {
  const [appliedPreFilters, setAppliedPreFilters] = useState({
    bookingStatusFilter: DEFAULT_PRE_FILTERS.bookingStatusFilter,
    bookingBeginningDate: DEFAULT_PRE_FILTERS.bookingBeginningDate,
    bookingEndingDate: DEFAULT_PRE_FILTERS.bookingEndingDate,
    offerEventDate: DEFAULT_PRE_FILTERS.offerEventDate,
    offerVenueId: location.state?.venueId || DEFAULT_PRE_FILTERS.offerVenueId,
    offerType: DEFAULT_PRE_FILTERS.offerType,
  })
  const [bookingsRecap, setBookingsRecap] = useState([])
  const [isDownloadingCSV, setIsDownloadingCSV] = useState(false)
  const [isTableLoading, setIsTableLoading] = useState(false)
  const [wereBookingsRequested, setWereBookingsRequested] = useState(false)
  const isBookingFiltersActive = useActiveFeature('ENABLE_NEW_BOOKING_FILTERS')

  const loadBookingsRecap = useCallback(
    async preFilters => {
      setIsTableLoading(true)
      setBookingsRecap([])
      setWereBookingsRequested(true)
      setAppliedPreFilters({ ...preFilters })

      const bookingsFilters = {
        page: 1,
        venueId: preFilters.offerVenueId,
        eventDate: preFilters.offerEventDate,
        bookingPeriodBeginningDate: preFilters.bookingBeginningDate,
        bookingPeriodEndingDate: preFilters.bookingEndingDate,
        bookingStatusFilter: preFilters.bookingStatusFilter,
        offerType: preFilters.offerType,
      }
      let filteredBookingsResponse
      try {
        filteredBookingsResponse = await pcapi.loadFilteredBookingsRecap(
          bookingsFilters
        )
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
        showNotification(
          'information',
          'L’affichage des réservations a été limité à 5 000 réservations. Vous pouvez modifier les filtres pour affiner votre recherche.'
        )
      }
    },
    [showNotification]
  )

  const downloadBookingsCSV = useCallback(
    async filters => {
      setIsDownloadingCSV(true)
      try {
        await downloadCSVFile(filters)
      } catch (e) {
        showNotification(
          'error',
          "Une erreur s'est produite. Veuillez réessayer ultérieurement."
        )
      }
      setIsDownloadingCSV(false)
    },
    [showNotification]
  )

  useEffect(() => {
    if (location.state?.statuses.length > 0) {
      loadBookingsRecap({
        bookingBeginningDate: DEFAULT_PRE_FILTERS.bookingBeginningDate,
        bookingEndingDate: DEFAULT_PRE_FILTERS.bookingEndingDate,
        bookingStatusFilter: DEFAULT_PRE_FILTERS.bookingStatusFilter,
        offerEventDate: DEFAULT_PRE_FILTERS.offerEventDate,
        offerVenueId:
          location.state?.venueId || DEFAULT_PRE_FILTERS.offerVenueId,
      })
    }
  }, [location.state, loadBookingsRecap])

  const werePreFiltersCustomized = useMemo(() => {
    return (
      appliedPreFilters.offerVenueId !== DEFAULT_PRE_FILTERS.offerVenueId ||
      appliedPreFilters.bookingBeginningDate !==
        DEFAULT_PRE_FILTERS.bookingBeginningDate ||
      appliedPreFilters.bookingEndingDate !==
        DEFAULT_PRE_FILTERS.bookingEndingDate ||
      appliedPreFilters.bookingStatusFilter !==
        DEFAULT_PRE_FILTERS.bookingStatusFilter ||
      appliedPreFilters.offerEventDate !== DEFAULT_PRE_FILTERS.offerEventDate
    )
  }, [
    appliedPreFilters.bookingStatusFilter,
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
      <h2 className="br-title">Affichage des réservations</h2>
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
        isBookingFiltersActive={isBookingFiltersActive}
        isDownloadingCSV={isDownloadingCSV}
        isTableLoading={isTableLoading}
        wereBookingsRequested={wereBookingsRequested}
      />
      {wereBookingsRequested ? (
        bookingsRecap.length > 0 ? (
          <BookingsRecapTable
            bookingsRecap={bookingsRecap}
            isBookingFiltersActive={isBookingFiltersActive}
            isLoading={isTableLoading}
            locationState={location.state}
          />
        ) : isTableLoading ? (
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
  showNotification: PropTypes.func.isRequired,
}

export default BookingsRecap
