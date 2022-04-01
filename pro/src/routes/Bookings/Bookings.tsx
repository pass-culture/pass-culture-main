import React, { useCallback, useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'
import { downloadCSVFile } from 'components/pages/Bookings/downloadCSVBookings'
import { DEFAULT_PRE_FILTERS } from 'components/pages/Bookings/PreFilters/_constants'
import { TPreFilters } from 'core/Bookings/types'
import * as pcapi from 'repository/pcapi/pcapi'
import BookingsScreen from 'screens/Bookings'

const MAX_LOADED_PAGES = 5

const Bookings = (): JSX.Element => {
  const location = useLocation<{ venueId: string; statuses: string[] }>()
  const notify = useNotification()
  const { currentUser: user } = useCurrentUser()

  const [bookingsRecap, setBookingsRecap] = useState([])
  const [isDownloadingCSV, setIsDownloadingCSV] = useState(false)
  const [isTableLoading, setIsTableLoading] = useState(false)
  const [wereBookingsRequested, setWereBookingsRequested] = useState(false)
  const isBookingFiltersActive = useActiveFeature('ENABLE_NEW_BOOKING_FILTERS')
  const [hasBooking, setHasBooking] = useState(true)

  const loadBookingsRecap = useCallback(
    async (preFilters: TPreFilters) => {
      setIsTableLoading(true)
      setBookingsRecap([])
      setWereBookingsRequested(true)

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
        notify.information(
          'L’affichage des réservations a été limité à 5 000 réservations. Vous pouvez modifier les filtres pour affiner votre recherche.'
        )
      }
    },
    [notify]
  )

  const checkUserHasBookings = useCallback(async () => {
    if (!user.isAdmin) {
      const { hasBookings } = await pcapi.getUserHasBookings()
      setHasBooking(hasBookings)
    }
  }, [user.isAdmin, setHasBooking])

  useEffect(() => {
    checkUserHasBookings()
  }, [checkUserHasBookings])

  const downloadBookingsCSV = useCallback(
    async filters => {
      setIsDownloadingCSV(true)
      try {
        await downloadCSVFile(filters)
      } catch (e) {
        notify.error(
          "Une erreur s'est produite. Veuillez réessayer ultérieurement."
        )
      }
      setIsDownloadingCSV(false)
    },
    [notify]
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
        offerType: DEFAULT_PRE_FILTERS.offerType,
      })
    }
  }, [location.state, loadBookingsRecap])

  return (
    <BookingsScreen
      bookingsRecap={bookingsRecap}
      downloadBookingsCSV={downloadBookingsCSV}
      hasBooking={hasBooking}
      isBookingFiltersActive={isBookingFiltersActive}
      isDownloadingCSV={isDownloadingCSV}
      isTableLoading={isTableLoading}
      loadBookingsRecap={loadBookingsRecap}
      locationState={location.state}
      setWereBookingsRequested={setWereBookingsRequested}
      venueId={location.state.venueId}
      wereBookingsRequested={wereBookingsRequested}
    />
  )
}

export default Bookings
