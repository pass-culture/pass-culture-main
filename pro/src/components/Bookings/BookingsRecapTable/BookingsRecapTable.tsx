import { useEffect, useMemo, useState } from 'react'
import { useLocation } from 'react-router'

import type {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Audience } from '@/commons/core/shared/types'
import { Table, TableVariant } from '@/ui-kit/Table/Table'

import { useCollectiveBookingsColumns } from './BookingsTable/ColumnsCollectiveBooking'
import { useBookingsTableColumnsByIndex } from './BookingsTable/ColumnsIndividualBooking'
import {
  ALL_BOOKING_STATUS,
  bookingIdOmnisearchFilter,
  DEFAULT_OMNISEARCH_CRITERIA,
  EMPTY_FILTER_VALUE,
} from './Filters/constants'
import { FilterByOmniSearch } from './Filters/FilterByOmniSearch'
import styles from './Filters/Filters.module.scss'
import { Header } from './Header/Header'
import type { BookingsFilters } from './types'
import { filterBookingsRecap } from './utils/filterBookingsRecap'

interface BookingsRecapTableProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
> {
  bookingsRecap: T[]
  isLoading: boolean
  locationState?: {
    statuses: string[]
  }
  audience: Audience
  resetBookings?: () => void
}

export const BookingsRecapTable = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
>({
  isLoading,
  locationState,
  audience,
  resetBookings,
  bookingsRecap: bookings,
}: BookingsRecapTableProps<T>) => {
  const { logEvent } = useAnalytics()

  const [filteredBookings, setFilteredBookings] = useState(bookings)

  const location = useLocation()
  const queryParams = new URLSearchParams(location.search)
  const [defaultBookingId, setDefaultBookingId] = useState(
    queryParams.get('bookingId') || EMPTY_FILTER_VALUE
  )

  const [filters, setFilters] = useState<BookingsFilters>({
    bookingBeneficiary: EMPTY_FILTER_VALUE,
    bookingToken: EMPTY_FILTER_VALUE,
    offerISBN: EMPTY_FILTER_VALUE,
    offerName: EMPTY_FILTER_VALUE,
    bookingStatus: locationState?.statuses.length
      ? locationState.statuses
      : [...ALL_BOOKING_STATUS],
    selectedOmniSearchCriteria: defaultBookingId
      ? bookingIdOmnisearchFilter.id
      : DEFAULT_OMNISEARCH_CRITERIA,
    keywords: defaultBookingId,
    bookingInstitution: EMPTY_FILTER_VALUE,
    bookingId: defaultBookingId,
  })

  useEffect(() => {
    applyFilters()
  }, [bookings])

  const updateGlobalFilters = (updatedFilters: Partial<BookingsFilters>) => {
    setFilters((filters) => {
      const newFilters = { ...filters, ...updatedFilters }
      applyFilters(newFilters)
      return newFilters
    })
  }

  const applyFilters = (filtersBookingResults?: BookingsFilters) => {
    const filtersToApply = filtersBookingResults || filters
    const bookingsRecapFiltered = filterBookingsRecap(bookings, filtersToApply)
    setFilteredBookings(bookingsRecapFiltered)
  }

  const resetAllFilters = () => {
    const filtersBookingResults = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
      bookingInstitution: EMPTY_FILTER_VALUE,
      bookingStatus: [...ALL_BOOKING_STATUS],
      keywords: '',
      selectedOmniSearchCriteria: DEFAULT_OMNISEARCH_CRITERIA,
      bookingId: EMPTY_FILTER_VALUE,
    }
    setFilters(filtersBookingResults)
    applyFilters(filtersBookingResults)
  }

  const updateFilters = (
    updatedFilter: Partial<BookingsFilters>,
    updatedSelectedContent: {
      keywords: string
      selectedOmniSearchCriteria: string
    }
  ) => {
    const { keywords, selectedOmniSearchCriteria } = updatedSelectedContent
    if (selectedOmniSearchCriteria === bookingIdOmnisearchFilter.id) {
      setDefaultBookingId('')
    }
    setFilters((filters) => ({
      ...filters,
      ...updatedFilter,
      keywords,
      selectedOmniSearchCriteria,
    }))
    applyFilters({
      ...filters,
      ...updatedFilter,
    })
  }

  const rows = useMemo(
    () =>
      filteredBookings.map(
        (b, i) =>
          ({ ...b, id: i }) as BookingRecapResponseModel & { id: number }
      ),
    [filteredBookings]
  )

  const [expanded, setExpanded] = useState<Set<number>>(
    new Set(
      queryParams.get('bookingId') ? [Number(queryParams.get('bookingId'))] : []
    )
  )

  const toggle = (i: string | number) =>
    setExpanded((prev) => {
      const numericId = typeof i === 'string' ? parseInt(i, 10) : i
      const next = new Set(prev)
      next.has(numericId) ? next.delete(numericId) : next.add(numericId)
      return next
    })

  const { columns: individualColumns, getFullRowContentIndividual } =
    useBookingsTableColumnsByIndex({
      bookings, // liste complète
      bookingStatuses: filters.bookingStatus,
      updateGlobalFilters, // (partial) -> void
      expandedIds: expanded,
      onToggle: toggle,
    })

  const { columns: collectiveColumns, getFullRowContentCollective } =
    useCollectiveBookingsColumns({
      bookings, // ✅ liste passée pour l'entête
      bookingStatuses: filters.bookingStatus,
      updateGlobalFilters, // optionnel; si absent, l'entête affiche juste "Statut"
      expandedIds: expanded,
      onToggle: toggle,
    })

  return (
    <div>
      <div className={styles['filters-wrapper']}>
        <FilterByOmniSearch
          isDisabled={isLoading}
          keywords={filters.keywords}
          selectedOmniSearchCriteria={filters.selectedOmniSearchCriteria}
          updateFilters={updateFilters}
          audience={audience}
        />
      </div>
      {filteredBookings.length !== 0 && (
        <Header
          bookingsRecapFilteredLength={filteredBookings.length}
          isLoading={isLoading}
          queryBookingId={defaultBookingId}
          resetBookings={resetBookings}
        />
      )}
      <>
        <Table
          title="Réservations individuelles"
          columns={
            audience === Audience.INDIVIDUAL
              ? individualColumns
              : collectiveColumns
          }
          data={rows} // rows have { id: index }
          isLoading={isLoading}
          variant={TableVariant.COLLAPSE}
          noData={{
            hasNoData: false,
            message: {
              icon: '',
              title: 'Vous n’avez aucune réservation pour le moment',
              subtitle: '',
            },
          }}
          noResult={{
            message: 'Aucune réservation trouvée pour votre recherche',
            resetMessage: 'Afficher toutes les réservations',
            onFilterReset: resetAllFilters,
          }}
          getFullRowContent={
            audience === Audience.INDIVIDUAL
              ? getFullRowContentIndividual
              : getFullRowContentCollective
          }
        />
      </>
    </div>
  )
}
