import { useCallback, useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router'

import { BookingStatusFilter } from '@/apiClient/v1/new'
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

export function useBookingsFilters() {
  const navigate = useNavigate()
  const location = useLocation()
  const currentRoute = useCurrentRoute()

  const [appliedPreFilters, setAppliedPreFilters] =
    useState<PreFiltersParams>(DEFAULT_PRE_FILTERS)

  const [selectedPreFilters, setSelectedPreFilters] =
    useState<PreFiltersParams>(DEFAULT_PRE_FILTERS)

  const [wereBookingsRequested, setWereBookingsRequested] = useState(false)
  const [urlParams, setUrlParams] =
    useState<PreFiltersParams>(DEFAULT_PRE_FILTERS)

  useEffect(() => {
    const urlSearchParams = new URLSearchParams(location.search)

    if (
      urlSearchParams.has('bookingStatusFilter') ||
      urlSearchParams.has('bookingBeginningDate') ||
      urlSearchParams.has('bookingEndingDate') ||
      urlSearchParams.has('offerType') ||
      urlSearchParams.has('offerEventDate') ||
      urlSearchParams.has('offererAddressId')
    ) {
      const next: PreFiltersParams = {
        offererAddressId:
          urlSearchParams.get('offererAddressId') ??
          DEFAULT_PRE_FILTERS.offererAddressId,
        bookingStatusFilter: (() => {
          const param = urlSearchParams.get('bookingStatusFilter')
          return isBookingStatusFilter(param)
            ? param
            : DEFAULT_PRE_FILTERS.bookingStatusFilter
        })(),
        bookingBeginningDate:
          urlSearchParams.get('bookingBeginningDate') ??
          (urlSearchParams.has('offerEventDate')
            ? ''
            : DEFAULT_PRE_FILTERS.bookingBeginningDate),
        bookingEndingDate:
          urlSearchParams.get('bookingEndingDate') ??
          (urlSearchParams.has('offerEventDate')
            ? ''
            : DEFAULT_PRE_FILTERS.bookingEndingDate),
        offerEventDate:
          urlSearchParams.get('offerEventDate') ??
          DEFAULT_PRE_FILTERS.offerEventDate,
      }
      setWereBookingsRequested(true)
      setAppliedPreFilters(next)
      setSelectedPreFilters(next)
    }
  }, [location.search])

  const hasPreFilters = useMemo(() => {
    let key: keyof PreFiltersParams
    for (key in selectedPreFilters) {
      const selectedValue = selectedPreFilters[key]
      const defaultValue = DEFAULT_PRE_FILTERS[key]
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
  }, [selectedPreFilters])

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
      ...(filter.offererAddressId
        ? { offererAddressId: filter.offererAddressId }
        : {}),
    } as Partial<PreFiltersParams>

    setUrlParams((prev) => ({ ...prev, ...partialUrlInfo }) as PreFiltersParams)

    navigate(`${currentRoute.pathname}?page=1&${stringify(partialUrlInfo)}`)
  }

  const applyNow = () => {
    setWereBookingsRequested(true)
    setAppliedPreFilters(selectedPreFilters)
    updateUrl(selectedPreFilters)
  }

  const applyPreFilters = (filters: PreFiltersParams) => {
    setAppliedPreFilters(filters)
  }

  const resetPreFilters = useCallback(() => {
    setWereBookingsRequested(false)
    setAppliedPreFilters(DEFAULT_PRE_FILTERS)
    setSelectedPreFilters(DEFAULT_PRE_FILTERS)
  }, [])

  const resetAndApplyPreFilters = () => {
    resetPreFilters()
    updateUrl({ ...DEFAULT_PRE_FILTERS })
  }

  return {
    appliedPreFilters,
    selectedPreFilters,
    wereBookingsRequested,
    urlParams,

    hasPreFilters,
    isRefreshRequired,

    updateSelectedFilters,
    applyNow,
    applyPreFilters,
    resetPreFilters,
    resetAndApplyPreFilters,
    updateUrl,
  }
}
