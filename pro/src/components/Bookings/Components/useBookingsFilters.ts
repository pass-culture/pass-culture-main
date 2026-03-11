import { useCallback, useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router'

import { BookingStatusFilter } from '@/apiClient/v1'
import { DEFAULT_PRE_FILTERS } from '@/commons/core/Bookings/constants'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { useCurrentRoute } from '@/commons/hooks/useCurrentRoute'
import { isDateValid } from '@/commons/utils/date'
import { isEqual } from '@/commons/utils/isEqual'
import { stringify } from '@/commons/utils/query-string'

function isBookingStatusFilter(
  value: string | null
): value is BookingStatusFilter {
  return (
    value !== null &&
    Object.values(BookingStatusFilter).includes(value as BookingStatusFilter)
  )
}

export function useBookingsFilters(
  params: { offererId?: string; offerVenueId?: string } = {}
) {
  const navigate = useNavigate()
  const location = useLocation()
  const currentRoute = useCurrentRoute()

  const initialAppliedFilters: PreFiltersParams = useMemo(
    () => ({
      ...DEFAULT_PRE_FILTERS,
      ...(params.offererId ? { offererId: params.offererId } : undefined),
      ...(params.offerVenueId
        ? { offerVenueId: params.offerVenueId }
        : undefined),
    }),
    [params.offererId, params.offerVenueId]
  )

  const [appliedPreFilters, setAppliedPreFilters] = useState<PreFiltersParams>(
    initialAppliedFilters
  )

  const [selectedPreFilters, setSelectedPreFilters] =
    useState<PreFiltersParams>(initialAppliedFilters)

  const [wereBookingsRequested, setWereBookingsRequested] = useState(false)
  const [urlParams, setUrlParams] = useState<PreFiltersParams>(
    initialAppliedFilters
  )

  useEffect(() => {
    const urlSearchParams = new URLSearchParams(location.search)

    if (
      urlSearchParams.has('offerVenueId') ||
      urlSearchParams.has('bookingStatusFilter') ||
      urlSearchParams.has('bookingBeginningDate') ||
      urlSearchParams.has('bookingEndingDate') ||
      urlSearchParams.has('offerType') ||
      urlSearchParams.has('offerEventDate') ||
      urlSearchParams.has('offererId') ||
      urlSearchParams.has('offererAddressId')
    ) {
      const next: PreFiltersParams = {
        offerVenueId:
          urlSearchParams.get('offerVenueId') ??
          initialAppliedFilters.offerVenueId,
        offererAddressId:
          urlSearchParams.get('offererAddressId') ??
          DEFAULT_PRE_FILTERS.offererAddressId,
        bookingStatusFilter: (() => {
          const param = urlSearchParams.get('bookingStatusFilter')
          return isBookingStatusFilter(param)
            ? param
            : initialAppliedFilters.bookingStatusFilter
        })(),
        bookingBeginningDate:
          urlSearchParams.get('bookingBeginningDate') ??
          (urlSearchParams.has('offerEventDate')
            ? ''
            : initialAppliedFilters.bookingBeginningDate),
        bookingEndingDate:
          urlSearchParams.get('bookingEndingDate') ??
          (urlSearchParams.has('offerEventDate')
            ? ''
            : initialAppliedFilters.bookingEndingDate),
        offerEventDate:
          urlSearchParams.get('offerEventDate') ??
          initialAppliedFilters.offerEventDate,
        offererId: initialAppliedFilters.offererId,
      }

      setAppliedPreFilters(next)
      setSelectedPreFilters(next)
    }
  }, [initialAppliedFilters, location.search])

  const hasPreFilters = useMemo(() => {
    let key: keyof PreFiltersParams
    for (key in selectedPreFilters) {
      const selectedValue = selectedPreFilters[key]
      const defaultValue = initialAppliedFilters[key]
      if (
        key.includes('Date') &&
        isDateValid(selectedValue) &&
        isDateValid(defaultValue)
      ) {
        if (
          new Date(selectedValue).getTime() !== new Date(defaultValue).getTime()
        ) {
          return true
        }
      } else if (selectedValue !== defaultValue) {
        return true
      }
    }
    return false
  }, [selectedPreFilters, initialAppliedFilters])

  const isRefreshRequired = useMemo(
    () =>
      !isEqual(selectedPreFilters, appliedPreFilters) && wereBookingsRequested,
    [selectedPreFilters, appliedPreFilters, wereBookingsRequested]
  )

  const updateSelectedFilters = useCallback(
    (updated: Partial<PreFiltersParams>) => {
      const next: Partial<PreFiltersParams> = { ...updated }

      if ('offerEventDate' in updated) {
        next.bookingBeginningDate = ''
        next.bookingEndingDate = ''
        if (updated.offerEventDate === appliedPreFilters.offerEventDate) {
          next.bookingBeginningDate = appliedPreFilters.bookingBeginningDate
          next.bookingEndingDate = appliedPreFilters.bookingEndingDate
        }
      }

      setSelectedPreFilters((curr) => ({ ...curr, ...next }))
    },
    [appliedPreFilters]
  )

  const updateUrl = (filter: PreFiltersParams) => {
    const partialUrlInfo = {
      bookingStatusFilter: filter.bookingStatusFilter,
      ...(filter.offerEventDate && filter.offerEventDate !== 'all'
        ? { offerEventDate: filter.offerEventDate }
        : {}),
      ...(filter.bookingBeginningDate
        ? { bookingBeginningDate: filter.bookingBeginningDate }
        : {}),
      ...(filter.bookingEndingDate
        ? { bookingEndingDate: filter.bookingEndingDate }
        : {}),
      ...(filter.offerVenueId ? { offerVenueId: filter.offerVenueId } : {}),
      ...(filter.offererAddressId
        ? { offererAddressId: filter.offererAddressId }
        : {}),
      ...(filter.offererId ? { offererId: filter.offererId } : {}),
    } as Partial<PreFiltersParams>

    setUrlParams((prev) => ({ ...prev, ...partialUrlInfo }) as PreFiltersParams)

    navigate(`${currentRoute.pathname}?page=1&${stringify(partialUrlInfo)}`)
  }

  const applyNow = () => {
    setAppliedPreFilters(selectedPreFilters)
    updateUrl(selectedPreFilters)
  }

  const applyPreFilters = (filters: PreFiltersParams) => {
    setAppliedPreFilters(filters)
  }

  const resetPreFilters = () => {
    setWereBookingsRequested(false)
    setAppliedPreFilters(initialAppliedFilters)
    setSelectedPreFilters(initialAppliedFilters)
  }

  const resetAndApplyPreFilters = () => {
    resetPreFilters()
    updateUrl({ ...initialAppliedFilters })
  }

  return {
    initialAppliedFilters,
    appliedPreFilters,
    selectedPreFilters,
    wereBookingsRequested,
    urlParams,

    hasPreFilters,
    isRefreshRequired,

    setWereBookingsRequested,
    updateSelectedFilters,
    applyNow,
    applyPreFilters,
    resetPreFilters,
    resetAndApplyPreFilters,
    updateUrl,
  }
}
