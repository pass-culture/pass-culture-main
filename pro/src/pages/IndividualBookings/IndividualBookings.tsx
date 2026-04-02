import { useEffect, useState } from 'react'
import { useLocation } from 'react-router'
import { formatAndOrderAddresses } from 'repository/venuesService'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  GetOffererAddressesWithOffersOption,
  GetVenueAddressesWithOffersOption,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import {
  GET_BOOKINGS_QUERY_KEY,
  GET_HAS_BOOKINGS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useOffererAddresses } from '@/commons/hooks/swr/useOffererAddresses'
import { useVenueAddresses } from '@/commons/hooks/swr/useVenueAddresses'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureCurrentOfferer } from '@/commons/store/offerer/selectors'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { isEqual } from '@/commons/utils/isEqual'
import { sanitizeBookingSearchTerm } from '@/commons/utils/sanitizeBookingSearchTerm'
import { ChoosePreFiltersMessage } from '@/components/Bookings/Components/ChoosePreFiltersMessage/ChoosePreFiltersMessage'
import { DownloadsMovedBanner } from '@/components/DownloadsMovedBanner/DownloadsMovedBanner'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import {
  ALL_BOOKING_STATUS,
  bookingIdOmnisearchFilter,
  DEFAULT_OMNISEARCH_CRITERIA,
  EMPTY_FILTER_VALUE,
} from '../../components/Bookings/Components/Filters/constants'
import { FilterByOmniSearch } from '../../components/Bookings/Components/Filters/FilterByOmniSearch'
import { Header } from '../../components/Bookings/Components/Header/Header'
import { PreFilters } from '../../components/Bookings/Components/PreFilters/PreFilters'
import type { BookingsFilters } from '../../components/Bookings/Components/types'
import { useBookingsFilters } from '../../components/Bookings/Components/useBookingsFilters'
import { IndividualBookingsTable } from '../../components/Bookings/IndividualBookingsTable/IndividualBookingsTable'
import {
  getFilteredIndividualBookingsAdapter,
  type OmniSearchParams,
} from './adapters/getFilteredIndividualBookingsAdapter'
import styles from './IndividualBookings.module.scss'

const buildOmniSearch = (filters: BookingsFilters): OmniSearchParams => {
  const result: OmniSearchParams = {}
  if (filters.offerName && filters.offerName !== EMPTY_FILTER_VALUE) {
    result.offerName = sanitizeBookingSearchTerm(filters.offerName)
  }
  if (
    filters.bookingBeneficiary &&
    filters.bookingBeneficiary !== EMPTY_FILTER_VALUE
  ) {
    result.beneficiaryNameOrEmail = sanitizeBookingSearchTerm(
      filters.bookingBeneficiary
    )
  }
  if (filters.offerISBN && filters.offerISBN !== EMPTY_FILTER_VALUE) {
    result.offerEan = filters.offerISBN.trim()
  }
  if (filters.bookingToken && filters.bookingToken !== EMPTY_FILTER_VALUE) {
    result.bookingToken = filters.bookingToken.trim().toLowerCase()
  }
  return result
}

export const IndividualBookings = () => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const selectedOfferer = useAppSelector(ensureCurrentOfferer)
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const {
    initialAppliedFilters,
    appliedPreFilters,
    selectedPreFilters,
    wereBookingsRequested,
    setWereBookingsRequested,
    urlParams,
    hasPreFilters,
    isRefreshRequired,
    updateSelectedFilters,
    applyNow,
    resetPreFilters,
    resetAndApplyPreFilters,
    updateUrl,
  } = useBookingsFilters(
    withSwitchVenueFeature
      ? { offerVenueId: selectedPartnerVenue.id.toString() }
      : { offererId: selectedOfferer.id.toString() }
  )

  const offererAddressQuery = useOffererAddresses(
    GetOffererAddressesWithOffersOption.INDIVIDUAL_OFFERS_ONLY
  )
  const venueAddressQuery = useVenueAddresses(
    GetVenueAddressesWithOffersOption.INDIVIDUAL_OFFERS_ONLY
  )
  const offererAddresses = formatAndOrderAddresses(
    withSwitchVenueFeature ? venueAddressQuery.data : offererAddressQuery.data
  )

  const queryParams = new URLSearchParams(location.search)
  const [defaultBookingId, setDefaultBookingId] = useState(
    queryParams.get('bookingId') || EMPTY_FILTER_VALUE
  )

  const [page, setPage] = useState(1)

  const [filters, setFilters] = useState<BookingsFilters>({
    bookingBeneficiary: EMPTY_FILTER_VALUE,
    bookingToken: EMPTY_FILTER_VALUE,
    offerISBN: EMPTY_FILTER_VALUE,
    offerName: EMPTY_FILTER_VALUE,
    bookingInstitution: EMPTY_FILTER_VALUE,
    bookingStatus: location.state?.statuses?.length
      ? location.state.statuses
      : [...ALL_BOOKING_STATUS],
    keywords: defaultBookingId,
    selectedOmniSearchCriteria: defaultBookingId
      ? bookingIdOmnisearchFilter.value
      : DEFAULT_OMNISEARCH_CRITERIA,
    bookingId: defaultBookingId,
  })

  const [omniSearchInput, setOmniSearchInput] = useState<OmniSearchParams>(
    buildOmniSearch(filters)
  )
  const [omniSearch, setOmniSearch] = useState<OmniSearchParams>(
    buildOmniSearch(filters)
  )

  useEffect(() => {
    const timeout = setTimeout(() => {
      setOmniSearch(omniSearchInput)
    }, 400)
    return () => clearTimeout(timeout)
  }, [omniSearchInput])

  const { data: bookingsResult, isLoading } = useSWR(
    isEqual(appliedPreFilters, initialAppliedFilters)
      ? null
      : [GET_BOOKINGS_QUERY_KEY, appliedPreFilters, page, omniSearch],
    async ([, filterParams, currentPage, search]) => {
      setWereBookingsRequested(true)
      return await getFilteredIndividualBookingsAdapter({
        ...filterParams,
        page: currentPage as number,
        ...(search as OmniSearchParams),
      })
    },
    {
      fallbackData: {
        bookings: [],
        pages: 0,
        total: 0,
        currentPage: 1,
      },
    }
  )

  const updateGlobalFilters = (updatedFilters: Partial<BookingsFilters>) => {
    setFilters((prev) => ({ ...prev, ...updatedFilters }))
  }

  const updateFilters = (
    updatedFilter: Partial<BookingsFilters>,
    updatedSelectedContent: {
      keywords: string
      selectedOmniSearchCriteria: string
    }
  ) => {
    const { keywords, selectedOmniSearchCriteria } = updatedSelectedContent
    if (selectedOmniSearchCriteria === bookingIdOmnisearchFilter.value) {
      setDefaultBookingId('')
    }
    const newFilters = {
      ...filters,
      ...updatedFilter,
      keywords,
      selectedOmniSearchCriteria,
    }
    setFilters(newFilters)
    setOmniSearchInput(buildOmniSearch(newFilters))
    setPage(1)
  }

  const applyFilters = () => {
    setPage(1)
    applyNow()
  }

  const resetFilters = () => {
    setPage(1)
    resetAndApplyPreFilters()
  }

  const { data: hasBookingsQuery, isLoading: hasBookingsQueryLoading } = useSWR(
    [GET_HAS_BOOKINGS_QUERY_KEY],
    () => api.getUserHasBookings()
  )

  const resetPreFiltersWithLog = () => {
    resetPreFilters()
    logEvent(Events.CLICKED_RESET_FILTERS, { from: location.pathname })
  }

  if (hasBookingsQueryLoading || !hasBookingsQuery) {
    return <Spinner />
  }

  return (
    <div>
      <PreFilters
        selectedPreFilters={selectedPreFilters}
        updateSelectedFilters={updateSelectedFilters}
        hasPreFilters={hasPreFilters}
        isRefreshRequired={isRefreshRequired}
        applyNow={applyFilters}
        resetPreFilters={resetPreFiltersWithLog}
        wereBookingsRequested={wereBookingsRequested}
        hasResult={isLoading || bookingsResult.total > 0}
        isFiltersDisabled={!hasBookingsQuery.hasBookings}
        isLocalLoading={offererAddressQuery.isLoading}
        isTableLoading={isLoading}
        offererAddresses={offererAddresses}
        urlParams={urlParams}
        updateUrl={updateUrl}
      />
      {withSwitchVenueFeature && wereBookingsRequested && (
        <div className={styles['downloads-banner']}>
          <DownloadsMovedBanner isIndividual={true} />
        </div>
      )}
      {(!withSwitchVenueFeature || wereBookingsRequested) && (
        <FilterByOmniSearch
          isDisabled={false}
          keywords={filters.keywords}
          selectedOmniSearchCriteria={filters.selectedOmniSearchCriteria}
          updateFilters={updateFilters}
        />
      )}
      {(isLoading || bookingsResult.total > 0) && (
        <Header
          bookingsRecapFilteredLength={bookingsResult.total}
          isLoading={isLoading}
          queryBookingId={defaultBookingId}
          resetBookings={resetFilters}
        />
      )}
      {hasBookingsQuery.hasBookings && !wereBookingsRequested ? (
        <ChoosePreFiltersMessage />
      ) : (
        <IndividualBookingsTable
          bookings={bookingsResult.bookings}
          bookingStatuses={filters.bookingStatus}
          updateGlobalFilters={updateGlobalFilters}
          resetFilters={resetFilters}
          isLoading={isLoading}
          hasNoBooking={!hasBookingsQuery.hasBookings}
          currentPage={page}
          pageCount={bookingsResult.pages}
          onPageChange={setPage}
        />
      )}
    </div>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualBookings
