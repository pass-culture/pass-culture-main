import React, { useCallback, useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { BookingRecapResponseModel } from 'api/v1/gen'
import useActiveFeature from 'components/hooks/useActiveFeature'
import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'
import { DEFAULT_PRE_FILTERS, TPreFilters } from 'core/Bookings'
import { Audience } from 'core/shared'
import BookingsScreen from 'screens/Bookings'

import {
  getBookingsCSVFileAdapter,
  getUserHasBookingsAdapter,
  getVenuesAdapter,
} from './adapters'
import getFilteredBookingsRecapAdapter from './adapters/getFilteredBookingsRecapAdapter'

const MAX_LOADED_PAGES = 5

const Bookings = (): JSX.Element => {
  const location = useLocation<{ venueId?: string; statuses?: string[] }>()
  const notify = useNotification()
  const { currentUser: user } = useCurrentUser()
  const separateIndividualAndCollectiveOffers = useActiveFeature(
    'ENABLE_INDIVIDUAL_AND_COLLECTIVE_OFFER_SEPARATION'
  )

  const [bookingsRecap, setBookingsRecap] = useState<
    BookingRecapResponseModel[]
  >([])
  const [isDownloadingCSV, setIsDownloadingCSV] = useState(false)
  const [isTableLoading, setIsTableLoading] = useState(false)
  const [wereBookingsRequested, setWereBookingsRequested] = useState(false)
  const isBookingFiltersActive = useActiveFeature('ENABLE_NEW_BOOKING_FILTERS')
  const [hasBooking, setHasBooking] = useState(true)
  const [isLocalLoading, setIsLocalLoading] = useState(false)
  const [venues, setVenues] = useState<{ id: string; displayName: string }[]>(
    []
  )

  const loadBookingsRecap = useCallback(
    async (preFilters: TPreFilters) => {
      setIsTableLoading(true)
      setBookingsRecap([])
      setWereBookingsRequested(true)

      const { isOk, message, payload } = await getFilteredBookingsRecapAdapter({
        ...preFilters,
        page: 1,
      })

      if (!isOk) {
        notify.error(message)
      }

      const { pages, bookingsRecap } = payload.bookings
      setBookingsRecap(bookingsRecap)

      let currentPage = 1
      while (currentPage < Math.min(pages, MAX_LOADED_PAGES)) {
        currentPage += 1
        const nextPageFilters = {
          ...preFilters,
          page: currentPage,
        }
        const { isOk, message, payload } =
          await getFilteredBookingsRecapAdapter(nextPageFilters)
        if (!isOk) {
          notify.error(message)
        }
        setBookingsRecap(currentBookingsRecap =>
          [...currentBookingsRecap].concat(payload.bookings.bookingsRecap)
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
      const { payload } = await getUserHasBookingsAdapter()
      setHasBooking(payload)
    }
  }, [user.isAdmin, setHasBooking])

  useEffect(() => {
    checkUserHasBookings()
  }, [checkUserHasBookings])

  const downloadBookingsCSV = useCallback(
    async (filters: TPreFilters) => {
      setIsDownloadingCSV(true)
      const { isOk, message } = await getBookingsCSVFileAdapter(filters)

      if (!isOk) {
        notify.error(message)
      }

      setIsDownloadingCSV(false)
    },
    [notify]
  )

  useEffect(() => {
    if (location.state?.statuses && location.state?.statuses?.length > 0) {
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

  useEffect(() => {
    async function fetchVenues() {
      setIsLocalLoading(true)
      const { isOk, message, payload } = await getVenuesAdapter()

      if (!isOk) {
        notify.error(message)
      }
      setVenues(payload.venues)
      setIsLocalLoading(false)
    }
    fetchVenues()
  }, [setIsLocalLoading, setVenues, notify])

  return (
    <BookingsScreen
      audience={Audience.INDIVIDUAL}
      bookingsRecap={bookingsRecap}
      downloadBookingsCSV={downloadBookingsCSV}
      hasBooking={hasBooking}
      isBookingFiltersActive={isBookingFiltersActive}
      isDownloadingCSV={isDownloadingCSV}
      isLocalLoading={isLocalLoading}
      isTableLoading={isTableLoading}
      loadBookingsRecap={loadBookingsRecap}
      locationState={location.state}
      separateIndividualAndCollectiveOffers={
        separateIndividualAndCollectiveOffers
      }
      setWereBookingsRequested={setWereBookingsRequested}
      venueId={location.state?.venueId}
      venues={venues}
      wereBookingsRequested={wereBookingsRequested}
    />
  )
}

export default Bookings
