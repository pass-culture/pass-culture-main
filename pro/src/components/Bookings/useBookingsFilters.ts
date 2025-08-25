import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSelector } from 'react-redux'

import { DEFAULT_PRE_FILTERS } from '@/commons/core/Bookings/constants'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { isDateValid } from '@/commons/utils/date'
import { isEqual } from '@/commons/utils/isEqual'

type UseBookingsFiltersArgs = {
  /** filters that are currently applied to the table (from parent/container) */
  appliedPreFilters: PreFiltersParams
  /** whether a search has already been performed (affects “refresh required” flag) */
  wereBookingsRequested: boolean
}

/**
 * Centralizes “selected filters” state + all derived booleans for the PreFilters UI.
 * - Mirrors applied filters into a local “selected” draft
 * - Computes whether something changed vs defaults (hasPreFilters)
 * - Computes refresh hint (isRefreshRequired)
 * - Encapsulates the “event date vs booking dates” coupling
 */
export function useBookingsFilters({
  appliedPreFilters,
  wereBookingsRequested,
}: UseBookingsFiltersArgs) {
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const initialAppliedFilters: PreFiltersParams = useMemo(
    () => ({
      ...DEFAULT_PRE_FILTERS,
      offererId: selectedOffererId?.toString() || '',
    }),
    [selectedOffererId]
  )

  // Local draft used by the form before the user clicks “Afficher”
  const [selectedPreFilters, setSelectedPreFilters] =
    useState<PreFiltersParams>({ ...appliedPreFilters })

  // Keep local draft in sync when parent changes (reset, url load, etc.)
  useEffect(() => {
    setSelectedPreFilters({ ...appliedPreFilters })
  }, [appliedPreFilters])

  // Has at least one filter deviated from defaults?
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
          new Date(selectedValue as string).getTime() !==
          new Date(defaultValue as string).getTime()
        ) {
          return true
        }
      } else if (selectedValue !== defaultValue) {
        return true
      }
    }
    return false
  }, [selectedPreFilters, initialAppliedFilters])

  // Do we need to prompt user to press “Afficher”?
  const isRefreshRequired = useMemo(
    () =>
      !isEqual(selectedPreFilters, appliedPreFilters) && wereBookingsRequested,
    [selectedPreFilters, appliedPreFilters, wereBookingsRequested]
  )

  // Single way to mutate the draft (handles the eventDate<->bookingDates rule)
  const updateSelectedFilters = useCallback(
    (updated: Partial<PreFiltersParams>) => {
      const next: Partial<PreFiltersParams> = { ...updated }

      if ('offerEventDate' in updated) {
        // When user sets an offerEventDate, wipe booking period
        next.bookingBeginningDate = ''
        next.bookingEndingDate = ''

        // If user picks the same value as already applied, restore booking period
        if (updated.offerEventDate === appliedPreFilters.offerEventDate) {
          next.bookingBeginningDate = appliedPreFilters.bookingBeginningDate
          next.bookingEndingDate = appliedPreFilters.bookingEndingDate
        }
      }

      setSelectedPreFilters((curr) => ({ ...curr, ...next }))
    },
    [appliedPreFilters]
  )

  return {
    // state
    selectedPreFilters,
    // derived
    hasPreFilters,
    isRefreshRequired,
    // actions
    setSelectedPreFilters,
    updateSelectedFilters,
  }
}
