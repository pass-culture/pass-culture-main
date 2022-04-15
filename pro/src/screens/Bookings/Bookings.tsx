import type { Location } from 'history'
import React, { useCallback, useState, useMemo, useEffect } from 'react'

import { BookingRecapResponseModel } from 'api/v1/gen'
import useActiveFeature from 'components/hooks/useActiveFeature'
import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import BookingsRecapTable from 'components/pages/Bookings/BookingsRecapTable/BookingsRecapTable'
import ChoosePreFiltersMessage from 'components/pages/Bookings/ChoosePreFiltersMessage/ChoosePreFiltersMessage'
import NoBookingsForPreFiltersMessage from 'components/pages/Bookings/NoBookingsForPreFiltersMessage/NoBookingsForPreFiltersMessage'
import {
  CollectiveBookingResponseModel,
  GetBookingsCSVFileAdapter,
  GetFilteredBookingsRecapAdapter,
  GetFilteredCollectiveBookingsRecapAdapter,
  GetUserHasBookingsAdapter,
  GetVenuesAdapter,
  TPreFilters,
} from 'core/Bookings'
import { DEFAULT_PRE_FILTERS } from 'core/Bookings'
import { Audience } from 'core/shared/types'
import NoData from 'new_components/NoData'
import Tabs from 'new_components/Tabs'

import PreFilters from './PreFilters'

interface IBookingsProps {
  locationState: Location['state']
  venueId?: string
  audience: Audience
  getBookingsCSVFileAdapter: GetBookingsCSVFileAdapter
  getFilteredBookingsRecapAdapter:
    | GetFilteredBookingsRecapAdapter
    | GetFilteredCollectiveBookingsRecapAdapter
  getUserHasBookingsAdapter: GetUserHasBookingsAdapter
  getVenuesAdapter: GetVenuesAdapter
}

const MAX_LOADED_PAGES = 5

const Bookings = ({
  locationState,
  venueId,
  audience,
  getBookingsCSVFileAdapter,
  getFilteredBookingsRecapAdapter,
  getUserHasBookingsAdapter,
  getVenuesAdapter,
}: IBookingsProps): JSX.Element => {
  const { currentUser: user } = useCurrentUser()
  const notify = useNotification()
  const isBookingFiltersActive = useActiveFeature('ENABLE_NEW_BOOKING_FILTERS')
  const separateIndividualAndCollectiveOffers = useActiveFeature(
    'ENABLE_INDIVIDUAL_AND_COLLECTIVE_OFFER_SEPARATION'
  )

  const [appliedPreFilters, setAppliedPreFilters] = useState<TPreFilters>({
    ...DEFAULT_PRE_FILTERS,
    offerVenueId: venueId || DEFAULT_PRE_FILTERS.offerVenueId,
  })
  const [isTableLoading, setIsTableLoading] = useState(false)
  const [bookings, setBookings] = useState<
    BookingRecapResponseModel[] | CollectiveBookingResponseModel[]
  >([])
  const [wereBookingsRequested, setWereBookingsRequested] = useState(false)
  const [hasBooking, setHasBooking] = useState(true)
  const [isLocalLoading, setIsLocalLoading] = useState(false)
  const [venues, setVenues] = useState<{ id: string; displayName: string }[]>(
    []
  )

  const werePreFiltersCustomized = useMemo(() => {
    const keys = Object.keys(
      appliedPreFilters
    ) as (keyof typeof DEFAULT_PRE_FILTERS)[]

    return keys.some(key => appliedPreFilters[key] !== DEFAULT_PRE_FILTERS[key])
  }, [appliedPreFilters])

  const resetPreFilters = useCallback(() => {
    setWereBookingsRequested(false)
    setAppliedPreFilters({ ...DEFAULT_PRE_FILTERS })
  }, [setWereBookingsRequested])

  const applyPreFilters = (filters: TPreFilters) => {
    setAppliedPreFilters(filters)
    loadBookingsRecap(filters)
  }

  const loadBookingsRecap = async (preFilters: TPreFilters) => {
    setIsTableLoading(true)
    setBookings([])
    setWereBookingsRequested(true)

    const { isOk, message, payload } = await getFilteredBookingsRecapAdapter({
      ...preFilters,
    })

    if (!isOk) {
      notify.error(message)
    }

    const { bookings, currentPage, pages } = payload

    setBookings(bookings)

    setIsTableLoading(false)
    if (currentPage === MAX_LOADED_PAGES && currentPage < pages) {
      notify.information(
        'L’affichage des réservations a été limité à 5 000 réservations. Vous pouvez modifier les filtres pour affiner votre recherche.'
      )
    }
  }

  const checkUserHasBookings = useCallback(async () => {
    if (!user.isAdmin) {
      const { payload } = await getUserHasBookingsAdapter()
      setHasBooking(payload)
    }
  }, [user.isAdmin, setHasBooking, getUserHasBookingsAdapter])

  useEffect(() => {
    checkUserHasBookings()
  }, [checkUserHasBookings])

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
  }, [setIsLocalLoading, setVenues, notify, getVenuesAdapter])

  return (
    <div className="bookings-page">
      <PageTitle title="Vos réservations" />
      <Titles title="Réservations" />
      {separateIndividualAndCollectiveOffers && (
        <Tabs
          collectiveLabel="Réservations collectives"
          collectiveLink="/reservations/collectives"
          individualLabel="Réservations individuelles"
          individualLink="/reservations"
          selectedAudience={audience}
        />
      )}
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
        applyPreFilters={applyPreFilters}
        getBookingsCSVFileAdapter={getBookingsCSVFileAdapter}
        hasResult={bookings.length > 0}
        isBookingFiltersActive={isBookingFiltersActive}
        isFiltersDisabled={!hasBooking}
        isLocalLoading={isLocalLoading}
        isTableLoading={isTableLoading}
        venues={venues}
        wereBookingsRequested={wereBookingsRequested}
      />
      {wereBookingsRequested ? (
        bookings.length > 0 ? (
          <BookingsRecapTable
            bookingsRecap={bookings}
            isBookingFiltersActive={isBookingFiltersActive}
            isLoading={isTableLoading}
            locationState={locationState}
          />
        ) : isTableLoading ? (
          <Spinner />
        ) : (
          <NoBookingsForPreFiltersMessage resetPreFilters={resetPreFilters} />
        )
      ) : hasBooking ? (
        <ChoosePreFiltersMessage />
      ) : (
        <NoData audience={audience} page="bookings" />
      )}
    </div>
  )
}

export default Bookings
