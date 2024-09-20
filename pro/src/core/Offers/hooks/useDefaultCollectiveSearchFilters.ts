import { CollectiveOfferDisplayedStatus } from 'apiClient/v1'
import { useActiveFeature } from 'hooks/useActiveFeature'

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
    const areCollectiveNewStatusesEnabled = useActiveFeature(
      'ENABLE_COLLECTIVE_NEW_STATUSES'
    )

    const defaultCollectiveSearchFilters = isNewOffersAndBookingsActive
      ? DEFAULT_COLLECTIVE_BOOKABLE_SEARCH_FILTERS
      : DEFAULT_COLLECTIVE_SEARCH_FILTERS

    return {
      ...defaultCollectiveSearchFilters,
      status: areCollectiveNewStatusesEnabled
        ? [
            ...defaultCollectiveSearchFilters.status,
            CollectiveOfferDisplayedStatus.REIMBURSED,
          ]
        : defaultCollectiveSearchFilters.status,
    }
  }
