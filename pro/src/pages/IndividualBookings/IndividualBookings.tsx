import { useMemo, useState } from 'react'
import { useLocation } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GetVenueAddressesWithOffersOption } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import {
  GET_BOOKINGS_QUERY_KEY,
  GET_HAS_BOOKINGS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { formatAndOrderAddresses } from '@/commons/format/venuesService'
import { useVenueAddresses } from '@/commons/hooks/swr/useVenueAddresses'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
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
import { filterBookingsRecap } from '../../components/Bookings/Components/utils/filterBookingsRecap'
import { IndividualBookingsTable } from '../../components/Bookings/IndividualBookingsTable/IndividualBookingsTable'
import { getFilteredIndividualBookingsAdapter } from './adapters/getFilteredIndividualBookingsAdapter'
import styles from './IndividualBookings.module.scss'

const MAX_LOADED_PAGES = 10

export const IndividualBookings = () => {
  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const {
    appliedPreFilters,
    selectedPreFilters,
    wereBookingsRequested,
    urlParams,
    hasPreFilters,
    isRefreshRequired,
    updateSelectedFilters,
    applyNow,
    resetPreFilters,
    resetAndApplyPreFilters,
    updateUrl,
  } = useBookingsFilters()
  const venueAddressQuery = useVenueAddresses(
    GetVenueAddressesWithOffersOption.INDIVIDUAL_OFFERS_ONLY
  )
  const offererAddresses = formatAndOrderAddresses(venueAddressQuery.data)

  const { data: bookingsQuery, isLoading } = useSWR(
    wereBookingsRequested ? [GET_BOOKINGS_QUERY_KEY, appliedPreFilters] : null,
    async ([, filterParams]) => {
      const { bookings, pages, currentPage } =
        await getFilteredIndividualBookingsAdapter(
          filterParams,
          selectedPartnerVenue.id
        )

      if (currentPage === MAX_LOADED_PAGES && currentPage < pages) {
        snackBar.success(
          'L’affichage des réservations a été limité à 5 000 réservations. Vous pouvez modifier les filtres pour affiner votre recherche.'
        )
      }

      return bookings
    },
    { fallbackData: [] }
  )

  // Omni-search state
  const queryParams = new URLSearchParams(location.search)
  const [defaultBookingId, setDefaultBookingId] = useState(
    queryParams.get('bookingId') || EMPTY_FILTER_VALUE
  )

  const baseOmniFilters: BookingsFilters = {
    bookingBeneficiary: EMPTY_FILTER_VALUE,
    bookingToken: EMPTY_FILTER_VALUE,
    offerISBN: EMPTY_FILTER_VALUE,
    offerName: EMPTY_FILTER_VALUE,
    bookingInstitution: EMPTY_FILTER_VALUE,
    bookingStatus: location.state?.statuses?.length
      ? location.state.statuses
      : [...ALL_BOOKING_STATUS],
    keywords: '',
    selectedOmniSearchCriteria: DEFAULT_OMNISEARCH_CRITERIA,
    bookingId: EMPTY_FILTER_VALUE,
  }

  const [filters, setFilters] = useState<BookingsFilters>({
    ...baseOmniFilters,
    // initialize from query if present
    selectedOmniSearchCriteria: defaultBookingId
      ? bookingIdOmnisearchFilter.value
      : DEFAULT_OMNISEARCH_CRITERIA,
    keywords: defaultBookingId,
    bookingId: defaultBookingId,
  })

  // Derive filtered list
  const filteredBookings = useMemo(
    () => filterBookingsRecap(bookingsQuery, filters),
    [bookingsQuery, filters]
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
    setFilters((prev) => ({
      ...prev,
      ...updatedFilter,
      keywords,
      selectedOmniSearchCriteria,
    }))
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
    <>
      <MainHeading mainHeading="Réservations individuelles" />

      <PreFilters
        selectedPreFilters={selectedPreFilters}
        updateSelectedFilters={updateSelectedFilters}
        hasPreFilters={hasPreFilters}
        isRefreshRequired={isRefreshRequired}
        applyNow={applyNow}
        resetPreFilters={resetPreFiltersWithLog}
        wereBookingsRequested={wereBookingsRequested}
        hasResult={(bookingsQuery ?? []).length > 0}
        isFiltersDisabled={!hasBookingsQuery.hasBookings}
        isLocalLoading={venueAddressQuery.isLoading}
        isTableLoading={isLoading}
        offererAddresses={offererAddresses}
        urlParams={urlParams}
        updateUrl={updateUrl}
      />
      {wereBookingsRequested && (
        <>
          <div className={styles['downloads-banner']}>
            <DownloadsMovedBanner isIndividual={true} />
          </div>
          <FilterByOmniSearch
            isDisabled={isLoading}
            keywords={filters.keywords}
            selectedOmniSearchCriteria={filters.selectedOmniSearchCriteria}
            updateFilters={updateFilters}
          />
        </>
      )}
      {filteredBookings.length !== 0 && (
        <Header
          bookingsRecapFilteredLength={filteredBookings.length}
          isLoading={isLoading}
          queryBookingId={defaultBookingId}
          resetBookings={resetAndApplyPreFilters}
        />
      )}
      {hasBookingsQuery.hasBookings && !wereBookingsRequested ? (
        <ChoosePreFiltersMessage />
      ) : (
        <IndividualBookingsTable
          bookings={filteredBookings}
          bookingStatuses={filters.bookingStatus}
          updateGlobalFilters={updateGlobalFilters}
          resetFilters={resetAndApplyPreFilters}
          isLoading={isLoading}
          hasNoBooking={!hasBookingsQuery.hasBookings}
        />
      )}
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualBookings
