import type { Location } from 'history'
import React, { useCallback, useEffect, useState } from 'react'
import { useHistory, useLocation } from 'react-router-dom'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
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
  DEFAULT_PRE_FILTERS,
  GetBookingsCSVFileAdapter,
  GetBookingsXLSFileAdapter,
  GetFilteredBookingsRecapAdapter,
  GetFilteredCollectiveBookingsRecapAdapter,
  GetUserHasBookingsAdapter,
  GetVenuesAdapter,
  TPreFilters,
} from 'core/Bookings'
import { Audience } from 'core/shared/types'
import { ReactComponent as LibraryIcon } from 'icons/library.svg'
import { ReactComponent as UserIcon } from 'icons/user.svg'
import NoData from 'new_components/NoData'
import Tabs from 'new_components/Tabs'

import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
} from '../../utils/date'
import { stringify } from '../../utils/query-string'

import PreFilters from './PreFilters'

interface IBookingsProps {
  locationState: Location['state']
  audience: Audience
  getBookingsCSVFileAdapter: GetBookingsCSVFileAdapter
  getBookingsXLSFileAdapter: GetBookingsXLSFileAdapter
  getFilteredBookingsRecapAdapter:
    | GetFilteredBookingsRecapAdapter
    | GetFilteredCollectiveBookingsRecapAdapter
  getUserHasBookingsAdapter: GetUserHasBookingsAdapter
  getVenuesAdapter: GetVenuesAdapter
}

const MAX_LOADED_PAGES = 5

const Bookings = ({
  locationState,
  audience,
  getBookingsCSVFileAdapter,
  getBookingsXLSFileAdapter,
  getFilteredBookingsRecapAdapter,
  getUserHasBookingsAdapter,
  getVenuesAdapter,
}: IBookingsProps): JSX.Element => {
  const { currentUser: user } = useCurrentUser()
  const notify = useNotification()
  const isBookingFiltersActive = useActiveFeature('ENABLE_NEW_BOOKING_FILTERS')

  const [appliedPreFilters, setAppliedPreFilters] = useState<TPreFilters>({
    ...DEFAULT_PRE_FILTERS,
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
  const [urlParams, setUrlParams] = useState<TPreFilters>(DEFAULT_PRE_FILTERS)

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
  const dateFilterFormat = (date: Date | string) =>
    formatBrowserTimezonedDateAsUTC(date, FORMAT_ISO_DATE_ONLY)

  const location = useLocation()
  const history = useHistory()

  useEffect(() => {
    const params = new URLSearchParams(location.search)
    const paramVenueId: string =
      params.get('offerVenueId') ?? DEFAULT_PRE_FILTERS.offerVenueId
    const paramBookingStatusFilter: string =
      params.get('bookingStatusFilter') ??
      DEFAULT_PRE_FILTERS.bookingStatusFilter
    const paramBookingBeginningDate: Date | null = !params.has(
      'bookingBeginningDate'
    )
      ? params.has('offerEventDate')
        ? null
        : DEFAULT_PRE_FILTERS.bookingBeginningDate
      : new Date(params.get('bookingBeginningDate') as string)
    const paramBookingEndingDate: Date | null = !params.has('bookingEndingDate')
      ? params.has('offerEventDate')
        ? null
        : DEFAULT_PRE_FILTERS.bookingEndingDate
      : new Date(params.get('bookingEndingDate') as string)
    const paramOfferType: string =
      params.get('offerType') ?? DEFAULT_PRE_FILTERS.offerType
    const paramOfferEventDate: string | Date = params.has('offerEventDate')
      ? params.get('offerEventDate') === 'all'
        ? 'all'
        : new Date(params.get('offerEventDate') as string)
      : DEFAULT_PRE_FILTERS.offerEventDate

    if (
      !(
        DEFAULT_PRE_FILTERS.offerVenueId === paramVenueId &&
        DEFAULT_PRE_FILTERS.bookingStatusFilter === paramBookingStatusFilter &&
        DEFAULT_PRE_FILTERS.offerEventDate === paramOfferEventDate &&
        DEFAULT_PRE_FILTERS.offerType === paramOfferType &&
        DEFAULT_PRE_FILTERS.bookingBeginningDate ===
          paramBookingBeginningDate &&
        DEFAULT_PRE_FILTERS.bookingEndingDate === paramBookingEndingDate
      )
    ) {
      const filterToLoad: TPreFilters = {
        offerVenueId: paramVenueId,
        bookingStatusFilter: paramBookingStatusFilter,
        bookingBeginningDate: paramBookingBeginningDate,
        bookingEndingDate: paramBookingEndingDate,
        offerType: paramOfferType,
        offerEventDate: paramOfferEventDate,
      } as TPreFilters

      loadBookingsRecap(filterToLoad)
      setAppliedPreFilters(filterToLoad)
    }
  }, [location])

  const updateUrl = (filter: TPreFilters) => {
    const partialUrlInfo = {
      ...(filter.offerEventDate && filter.offerEventDate !== 'all'
        ? { offerEventDate: dateFilterFormat(filter.offerEventDate) }
        : {}),
      ...(filter.bookingBeginningDate
        ? {
            bookingBeginningDate: dateFilterFormat(filter.bookingBeginningDate),
          }
        : {}),
      ...(filter.bookingEndingDate
        ? { bookingEndingDate: dateFilterFormat(filter.bookingEndingDate) }
        : {}),
      ...(filter.bookingStatusFilter
        ? { bookingStatusFilter: filter.bookingStatusFilter }
        : {}),
      ...(filter.offerType ? { offerType: filter.offerType } : {}),
      ...(filter.offerVenueId ? { offerVenueId: filter.offerVenueId } : {}),
    } as Partial<TPreFilters>
    setUrlParams({
      ...urlParams,
      ...partialUrlInfo,
    })
    history.push(
      `/reservations${
        audience === Audience.COLLECTIVE ? '/collectives' : ''
      }?page=1&${stringify(partialUrlInfo)}`
    )
  }
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
      <Tabs
        selectedKey={audience}
        tabs={[
          {
            label: 'Réservations individuelles',
            url: '/reservations',
            key: 'individual',
            Icon: UserIcon,
          },
          {
            label: 'Réservations collectives',
            url: '/reservations/collectives',
            key: 'collective',
            Icon: LibraryIcon,
          },
        ]}
      />
      <PreFilters
        appliedPreFilters={appliedPreFilters}
        applyPreFilters={applyPreFilters}
        getBookingsCSVFileAdapter={getBookingsCSVFileAdapter}
        getBookingsXLSFileAdapter={getBookingsXLSFileAdapter}
        hasResult={bookings.length > 0}
        isBookingFiltersActive={isBookingFiltersActive}
        isFiltersDisabled={!hasBooking}
        isLocalLoading={isLocalLoading}
        isTableLoading={isTableLoading}
        resetPreFilters={resetPreFilters}
        venues={venues}
        urlParams={urlParams}
        updateUrl={updateUrl}
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
