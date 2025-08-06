import { useActiveFeature } from '@/commons/hooks/useActiveFeature'

import {
  DEFAULT_COLLECTIVE_BOOKABLE_SEARCH_FILTERS,
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
} from '../constants'
import { CollectiveSearchFiltersParams } from '../types'

export const useDefaultCollectiveSearchFilters =
  (): CollectiveSearchFiltersParams => {
    const isNewOffersAndBookingsActive = useActiveFeature(
      'WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'
    )

    return isNewOffersAndBookingsActive
      ? DEFAULT_COLLECTIVE_BOOKABLE_SEARCH_FILTERS
      : DEFAULT_COLLECTIVE_SEARCH_FILTERS
  }
